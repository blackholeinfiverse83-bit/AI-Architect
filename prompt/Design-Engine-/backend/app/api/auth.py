from datetime import datetime, timedelta
from typing import Optional

from app.config import settings
from app.database_mongodb import get_database
from app.auth import hash_password, verify_password
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()

# Models
class UserSignUp(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    token: str
    user: dict

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

@router.post("/signup", response_model=Token)
async def signup(user_data: UserSignUp):
    db = get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = {
        "name": user_data.name,
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(new_user)
    user_id = str(result.inserted_id)
    
    # Generate token
    token_data = {"id": user_id, "email": user_data.email}
    access_token = create_access_token(data=token_data)
    
    return {
        "token": access_token,
        "user": {
            "id": user_id,
            "name": user_data.name,
            "email": user_data.email
        }
    }

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    db = get_database()
    
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = str(user["_id"])
    
    # Generate token
    token_data = {"id": user_id, "email": user["email"]}
    access_token = create_access_token(data=token_data)
    
    return {
        "token": access_token,
        "user": {
            "id": user_id,
            "name": user.get("name", ""),
            "email": user["email"]
        }
    }

from app.auth_mongodb import get_current_user
from bson import ObjectId

@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):
    """Verify auth token and return current user info"""
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    return {
        "user": {
            "id": str(user["_id"]),
            "name": user.get("name", ""),
            "email": user["email"]
        }
    }
