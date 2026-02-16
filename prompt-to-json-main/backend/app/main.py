import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time

import sentry_sdk
from app.api import (
    auth,
    generate,
    geometry_generator,
    health,
    video,
)

# BHIV AI Assistant: Both bhiv_assistant.py and bhiv_integrated.py are included
# bhiv_assistant.py: Main orchestration layer (/bhiv/v1/prompt)
# bhiv_integrated.py: Integrated design endpoint (/bhiv/v1/design)
from app.config import settings
from app.database import get_current_user, get_db
# Removed multi-city support - keeping only dashboard, geometry, and video
from app.utils import setup_logging
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sqlalchemy.orm import Session

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(),
        ],
        traces_sample_rate=1.0,
        environment=settings.ENVIRONMENT,
        send_default_pii=True,
    )
    logger.info("✅ Sentry initialized and connected")
else:
    logger.warning("❌ Sentry not configured")

# Lazy GPU detection - only when needed
try:
    from app.gpu_detector import gpu_detector

    logger.info("GPU detector loaded (detection deferred)")
except ImportError:
    logger.info("GPU detector not available - using CPU mode")

# Lazy Supabase connection - only when needed
try:
    from supabase import create_client

    logger.info(f"Supabase client loaded (connection deferred): {settings.SUPABASE_URL}")
except Exception as e:
    logger.error(f"❌ Supabase client loading failed: {e}")

# Check Yotta configuration
if settings.YOTTA_API_KEY and settings.YOTTA_URL:
    logger.info(f"✅ Yotta configured: {settings.YOTTA_URL}")
else:
    logger.warning("❌ Yotta not configured")

# Lazy initialization - validate on first use
try:
    from app.database_validator import validate_database
    from app.storage_manager import ensure_storage_ready

    logger.info("Storage and database modules loaded (validation deferred)")
except Exception as e:
    logger.error(f"❌ Storage/Database module loading failed: {e}")

# JWT Security scheme
security = HTTPBearer()

# Demo/Production mode: Hide internal endpoints from OpenAPI
IS_DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

app = FastAPI(
    title="Design Engine API",
    description="Complete FastAPI backend for design generation with JWT authentication",
    version="0.1.0",
    # Disable docs in demo mode
    docs_url="/docs" if not IS_DEMO_MODE else None,
    redoc_url="/redoc" if not IS_DEMO_MODE else None,
    openapi_url="/openapi.json" if not IS_DEMO_MODE else None,
)


# Startup event to ensure logging is working
@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 70)
    print("🚀 Design Engine API Server Starting...")
    print(f"🌍 Server URL: http://0.0.0.0:8000")
    print(f"📄 API Docs: http://0.0.0.0:8000/docs")
    print(f"🔍 Health Check: http://0.0.0.0:8000/health")
    print("📝 Request logging is ENABLED")
    print("=" * 70 + "\n")
    logger.info("🚀 Design Engine API Server Started Successfully")


# Global exception handler for consistent error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    print(f"⚠️ HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": exc.detail, "status_code": exc.status_code}},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    import traceback

    error_details = traceback.format_exc()
    logger.error(f"Unhandled exception: {exc}\n{error_details}", exc_info=True)
    print(f"❌ EXCEPTION: {exc}\n{error_details}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": str(exc), "status_code": 500}},
    )


# Essential metrics only for BHIV automations
if settings.ENABLE_METRICS:
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        excluded_handlers=["/metrics", "/docs", "/openapi.json"],
        env_var_name="ENABLE_METRICS",
    )
    instrumentator.instrument(app).expose(app, tags=["📊 Metrics"])
    logger.info("✅ Essential metrics enabled")
else:
    logger.info("📊 Metrics disabled")

# CORS middleware - Updated with actual frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Alternative dev port
        "http://127.0.0.1:8000",  # Local backend
        "https://samrachna-frontend.onrender.com",  # Production frontend (Render)
        "https://staging.bhiv.com",  # Staging (update with actual)
        "https://app.bhiv.com",  # Production (update with actual)
        "*",  # Keep for development - remove in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Force-Update"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log incoming request with print and logger
    request_log = f"🌐 {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}"
    print(request_log)
    logger.info(request_log)

    response = await call_next(request)

    # Log response with timing
    process_time = time.time() - start_time
    status_emoji = "✅" if 200 <= response.status_code < 300 else "❌" if response.status_code >= 400 else "⚠️"
    response_log = f"{status_emoji} {request.method} {request.url.path} → {response.status_code} ({process_time:.3f}s)"
    print(response_log)
    logger.info(response_log)

    return response


# ============================================================================
# STATIC FILE SERVING
# ============================================================================

# Mount static files for geometry previews
try:
    import os

    geometry_dir = os.path.join(os.path.dirname(__file__), "..", "data", "geometry_outputs")
    geometry_dir = os.path.abspath(geometry_dir)

    if os.path.exists(geometry_dir):
        app.mount("/static/geometry", StaticFiles(directory=geometry_dir), name="geometry")
        logger.info(f"✅ Static geometry files mounted at /static/geometry -> {geometry_dir}")
    else:
        os.makedirs(geometry_dir, exist_ok=True)
        app.mount("/static/geometry", StaticFiles(directory=geometry_dir), name="geometry")
        logger.info(f"✅ Created and mounted geometry directory: {geometry_dir}")
except Exception as e:
    logger.warning(f"⚠️ Static files mount failed: {e}")

# ============================================================================
# PUBLIC ENDPOINTS (No Authentication Required)
# ============================================================================


# Basic public health check
@app.get("/health", tags=["📊 Public Health"])
async def basic_health_check():
    """Basic health check - no authentication required"""
    return {"status": "ok", "service": "Design Engine API", "version": "0.1.0"}


# Authentication endpoints (PUBLIC - visible in docs)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["🔐 Authentication"])

# ============================================================================
# PROTECTED ENDPOINTS (JWT Authentication Required)
# ============================================================================

# 1. System Health & Monitoring (HIDDEN from docs)
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["📊 System Health"],
    dependencies=[Depends(get_current_user)],
    include_in_schema=False,
)

# 2. Core Design Generation (for Dashboard) - PUBLIC - visible in docs
app.include_router(
    generate.router, prefix="/api/v1", tags=["🎨 Design Generation"], dependencies=[Depends(get_current_user)]
)

# 3. 3D Geometry Generation (PUBLIC - visible in docs)
app.include_router(geometry_generator.router, dependencies=[Depends(get_current_user)])

# 4. Video Generation (PUBLIC - visible in docs)
app.include_router(video.router, prefix="/api/v1/video", tags=["🎬 Video Generation"])


# Note: /api/v1/rl/feedback/city/{city}/summary endpoint is handled by rl.router


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
