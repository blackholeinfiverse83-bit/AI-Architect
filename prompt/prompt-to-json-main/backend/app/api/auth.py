"""
Authentication API Endpoints
Login & Signup against the AI News Supabase "User" table (email-based auth)
"""
from datetime import datetime, timedelta, timezone
import uuid

from jose import jwt
from app.auth import hash_password, verify_password, create_access_token
from app.config import settings
from app.database import get_db, Base
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

router = APIRouter()
security = HTTPBearer()


# ============================================================================
# AI NEWS USER MODEL — maps to existing public."User" table
# ============================================================================

class NewsUser(Base):
    """Maps to the existing AI News 'User' table (capital U, quoted)"""
    __tablename__ = "User"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    isEmailVerified = Column(Boolean, default=False)
    emailVerifiedAt = Column(DateTime, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    lastLoginAt = Column(DateTime, nullable=True)
    isActive = Column(Boolean, default=True)


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class SignupRequest(BaseModel):
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, max_length=128, description="Password (min 6 chars)")
    name: str = Field(default="", max_length=100, description="Full name (optional)")


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    name: str = ""
    message: str


# ============================================================================
# AUTH INFO (for debugging: confirm auth router is mounted)
# ============================================================================

@router.get("", include_in_schema=False)
async def auth_info():
    """Confirm auth routes are available (GET /api/v1/auth)."""
    return {
        "message": "Auth routes are active",
        "signup": "POST /api/v1/auth/signup",
        "login": "POST /api/v1/auth/login",
        "login_form": "POST /api/v1/auth/login/form",
    }


# ============================================================================
# SIGNUP ENDPOINT
# ============================================================================

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - **email**: Email address (unique)
    - **password**: Password (min 6 chars)
    - **name**: Display name (optional)
    """
    # Check if email already exists
    existing_user = db.query(NewsUser).filter(NewsUser.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "EMAIL_TAKEN",
                    "message": "An account with this email already exists",
                    "status_code": 409,
                }
            },
        )

    # Create new user
    now = datetime.utcnow()
    new_user = NewsUser(
        id=uuid.uuid4(),
        email=request.email,
        password=hash_password(request.password),
        name=request.name or request.email.split("@")[0],
        isEmailVerified=False,
        isActive=True,
        createdAt=now,
        updatedAt=now,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    token = create_access_token(str(new_user.id))

    return AuthResponse(
        access_token=token,
        email=new_user.email,
        name=new_user.name or "",
        message="Account created successfully",
    )


# ============================================================================
# LOGIN ENDPOINT
# ============================================================================

class LoginRequest(BaseModel):
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=1, description="Password")


# ============================================================================
# LOGIN ENDPOINT (JSON body)
# ============================================================================

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with email and password (JSON body).
    Returns JWT access token on success.
    """
    user = db.query(NewsUser).filter(NewsUser.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password",
                    "status_code": 401,
                }
            },
        )

    # Verify password
    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password",
                    "status_code": 401,
                }
            },
        )

    # Check if user is active
    if user.isActive is False:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "ACCOUNT_DISABLED",
                    "message": "This account has been disabled",
                    "status_code": 403,
                }
            },
        )

    # Update last login
    user.lastLoginAt = datetime.utcnow()
    user.updatedAt = datetime.utcnow()
    db.commit()

    # Generate JWT token
    token = create_access_token(str(user.id))

    return {
        "access_token": token,
        "token_type": "bearer",
        "email": user.email,
        "name": user.name or "",
    }


# ============================================================================
# LOGIN ENDPOINT (form data — kept for backwards compatibility)
# ============================================================================

@router.post("/login/form")
async def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user with form-encoded email+password (OAuth2 compatible).
    The 'username' field is treated as email.
    """
    email = form_data.username

    # Find user by email
    user = db.query(NewsUser).filter(NewsUser.email == email).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password",
                    "status_code": 401,
                }
            },
        )

    # Verify password
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password",
                    "status_code": 401,
                }
            },
        )

    # Check if user is active
    if user.isActive is False:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "ACCOUNT_DISABLED",
                    "message": "This account has been disabled",
                    "status_code": 403,
                }
            },
        )

    # Update last login
    user.lastLoginAt = datetime.utcnow()
    user.updatedAt = datetime.utcnow()
    db.commit()

    # Generate JWT token
    token = create_access_token(str(user.id))

    return {
        "access_token": token,
        "token_type": "bearer",
        "email": user.email,
        "name": user.name or "",
    }


# ============================================================================
# REFRESH TOKEN ENDPOINT
# ============================================================================

@router.post("/refresh")
async def refresh_token(token: str = Depends(security)):
    """Refresh JWT token - requires valid existing token"""
    try:
        token_str = token.credentials

        payload = jwt.decode(token_str, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Create new JWT token
        token_data = {
            "sub": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        }
        new_token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return {"access_token": new_token, "token_type": "bearer"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except (jwt.JWTError):
        raise HTTPException(status_code=401, detail="Invalid token")
