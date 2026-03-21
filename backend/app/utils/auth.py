from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from ..config import get_settings

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.app_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            settings.app_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        return None


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=401,
            detail="未提供认证令牌",
        )
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="令牌无效或已过期",
        )
    return payload
