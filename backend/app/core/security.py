from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings
import secrets
import string

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _truncate_bcrypt(password: str, max_bytes: int = 72) -> str:
    """Truncate a password to bcrypt's 72-byte limit safely in UTF-8.
    This prevents passlib from raising when inputs exceed the limit.
    """
    try:
        data = password.encode("utf-8")
    except Exception:
        return password
    if len(data) <= max_bytes:
        return password
    return data[:max_bytes].decode("utf-8", errors="ignore")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash, honoring bcrypt's 72-byte limit."""
    safe = _truncate_bcrypt(plain_password)
    return pwd_context.verify(safe, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password, honoring bcrypt's 72-byte limit."""
    safe = _truncate_bcrypt(password)
    return pwd_context.hash(safe)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_referral_token() -> str:
    """Generate a unique referral token"""
    return generate_secure_token(36)


def generate_receipt_uuid() -> str:
    """Generate a unique receipt UUID"""
    return generate_secure_token(36)
