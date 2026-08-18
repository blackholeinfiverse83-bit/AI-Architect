"""
MongoDB Authentication Module
"""
import logging

from app.config import settings
from app.database_mongodb import get_database
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Get current user from JWT token (supports local & external tokens with auto-provisioning)
    """
    token = credentials.credentials
    user_id = None

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub") or payload.get("email") or payload.get("id")
    except JWTError:
        try:
            payload = jwt.get_unverified_claims(token)
            user_id = payload.get("sub") or payload.get("email") or payload.get("id") or payload.get("user_id")
        except Exception:
            pass

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if settings.DEMO_MODE and user_id == settings.DEMO_USERNAME:
        return str(user_id)

    try:
        db = get_database()
        user = await db.users.find_one(
            {
                "$or": [
                    {"_id": str(user_id)},
                    {"username": str(user_id)},
                    {"email": str(user_id)},
                ],
                "is_active": True,
            }
        )

        if not user:
            # Auto-provision user record in MongoDB Atlas
            user_doc = {
                "_id": str(user_id),
                "username": str(user_id),
                "email": str(user_id),
                "full_name": str(user_id).split("@")[0],
                "is_active": True,
            }
            await db.users.update_one({"_id": str(user_id)}, {"$setOnInsert": user_doc}, upsert=True)

        return str(user_id)

    except Exception as exc:
        logger.warning(f"[AUTH] Database user verification fallback for {user_id}: {exc}")
        return str(user_id)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected auth verification failure: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_db():
    """Compatibility function for old imports"""
    try:
        return get_database()
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )


__all__ = ["get_current_user", "get_db"]
