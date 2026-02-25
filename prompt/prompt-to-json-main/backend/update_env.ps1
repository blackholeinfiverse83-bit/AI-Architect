# PowerShell script to update .env file with complete configuration
# Run this script: .\update_env.ps1

$envContent = @"
# ============================================================================
# BHIV AI ASSISTANT - ENVIRONMENT CONFIGURATION
# ============================================================================

# ============================================================================
# APPLICATION
# ============================================================================
APP_NAME=BHIV AI Assistant
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# ============================================================================
# DATABASE (PostgreSQL via Supabase)
# ============================================================================
DATABASE_URL=postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# ============================================================================
# SUPABASE STORAGE
# ============================================================================
SUPABASE_URL=https://dntmhjlbxirtgslzwbui.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRudG1oamxieGlydGdzbHp3YnVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwMDc1OTksImV4cCI6MjA3MzU4MzU5OX0.e4ruUJBlI3WaS1RHtP-1844ZZz658MCkVqFMI9FP4GA

# Storage Buckets
STORAGE_BUCKET_FILES=files
STORAGE_BUCKET_PREVIEWS=previews
STORAGE_BUCKET_GEOMETRY=geometry
STORAGE_BUCKET_COMPLIANCE=compliance

# ============================================================================
# JWT AUTHENTICATION
# ============================================================================
JWT_SECRET_KEY=bhiv-jwt-secret-2024-must-be-at-least-32-characters-long
JWT_SECRET=bhiv-jwt-secret-2024-must-be-at-least-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30

# ============================================================================
# EXTERNAL SERVICES
# ============================================================================
SOHUM_MCP_URL=https://ai-rule-api-w7z5.onrender.com
SOHAM_URL=https://ai-rule-api-w7z5.onrender.com
RANJEET_RL_URL=https://land-utilization-rl.onrender.com
LAND_UTILIZATION_ENABLED=true

# ============================================================================
# LANGUAGE MODEL CONFIGURATION (AI/ML)
# ============================================================================

# AI Model Toggle - Set to true to use real AI models
USE_AI_MODEL=true

# Provider Selection
LM_PROVIDER=groq
DEVICE_PREFERENCE=auto

# ============================================================================
# AI API KEYS
# ============================================================================

# Groq (Llama 3.3 70B - FAST & FREE) - ACTIVE
GROQ_API_KEY=your-groq-api-key-here

# Tripo AI (3D Model Generation - 10 FREE/month)
TRIPO_API_KEY=your-tripo-api-key-here

# Meshy AI (3D Model Generation)
MESHY_API_KEY=your-meshy-api-key-here

# Hugging Face (3D Model Generation - UNLIMITED FREE)
HUGGINGFACE_API_KEY=your-huggingface-api-key-here

# ============================================================================
# Local GPU (Fallback)
# ============================================================================
LOCAL_GPU_ENABLED=true
LOCAL_GPU_DEVICE=cuda:0
LOCAL_GPU_MODEL=gpt2
MAX_PROMPT_LENGTH=2048

# ============================================================================
# MONITORING
# ============================================================================
SENTRY_DSN=https://4465443c7756d19300022e0d12f400e2@o4510289261887488.ingest.us.sentry.io/4510322463670272
SENTRY_ENVIRONMENT=development
LOG_LEVEL=INFO
METRICS_ENABLED=true

# ============================================================================
# REDIS CACHING
# ============================================================================
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# ============================================================================
# RATE LIMITING
# ============================================================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# ============================================================================
# MULTI-CITY CONFIGURATION
# ============================================================================
SUPPORTED_CITIES=["Mumbai","Pune","Ahmedabad","Nashik","Bangalore"]
DEFAULT_CITY=Mumbai

# ============================================================================
# RL CONFIGURATION
# ============================================================================
RL_ENABLED=true
RL_FEEDBACK_THRESHOLD=10

# ============================================================================
# DEMO CONFIGURATION
# ============================================================================
DEMO_USERNAME=admin
DEMO_PASSWORD=bhiv2024

# Demo Mode - Controls API documentation visibility
# false = Show all endpoints in Swagger (development)
# true = Hide internal endpoints from Swagger (production/demo)
DEMO_MODE=false
"@

# Write to .env file
$envContent | Out-File -FilePath ".env" -Encoding utf8 -NoNewline
Write-Host ".env file updated successfully!" -ForegroundColor Green
Write-Host "Location: $PWD\.env" -ForegroundColor Cyan
