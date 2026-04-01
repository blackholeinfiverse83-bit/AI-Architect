"""
auth.py — removed local JWT system.
All authentication is handled by the external AI-Being backend (ai-being-ecwj.onrender.com).
Token verification is done in auth_mongodb.py via signature-less JWT decode.
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
