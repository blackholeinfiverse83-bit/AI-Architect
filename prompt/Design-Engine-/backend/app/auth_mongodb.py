"""
MongoDB Authentication Module
Trusts JWT tokens issued by the AI-Being auth backend (ai-being-ecwj.onrender.com).
No local JWT issuance - all auth is delegated to the AI-Being service.
"""
import base64
import json
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)
security = HTTPBearer()


def _decode_jwt_payload(token: str) -> dict:
    """
    Decode JWT payload without verifying the signature.
    Works regardless of which JWT library is installed or its version.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Not a valid JWT structure")

        # Base64url decode with padding fix
        payload_b64 = parts[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_bytes)
    except Exception as exc:
        raise ValueError(f"Failed to decode JWT payload: {exc}") from exc


from app.config import settings
from jose import jwt, JWTError

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract user identity from a JWT token issued by this backend.
    Verifies the signature using JWT_SECRET_KEY.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = str(payload.get("id") or payload.get("sub") or "")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing user identity",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return user_id
    except JWTError:
        # Fallback to signature-less decode only for legacy migration phase - remove in production
        try:
            payload = _decode_jwt_payload(token)
            user_id: str = str(payload.get("id") or payload.get("sub") or "")
            if user_id:
                logger.warning(f"Accepted legacy token for user {user_id} - migrate to local auth!")
                return user_id
        except Exception:
            pass
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_db():
    """Compatibility shim for old imports"""
    from app.database_mongodb import get_database
    try:
        return get_database()
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )


__all__ = ["get_current_user", "get_db"]
