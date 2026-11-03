import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from app.core.config import settings

ph = PasswordHasher()

def get_password_hash(password: str) -> str:
    """Hash a password using Argon2id"""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against Argon2 hash"""
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError):
        return False

def hash_token(token: str) -> str:
    """Create SHA-256 hash of a refresh token for safe storage"""
    return hashlib.sha256(token.encode()).hexdigest()

def create_access_token(subject: Union[str, Any], roles: list[str], user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(subject),
        "user_id": user_id,
        "roles": roles,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(subject: Union[str, Any], user_id: int) -> tuple[str, str, datetime]:
    """Generate raw refresh token, its SHA256 hash, and expiration date"""
    raw_token = secrets.token_urlsafe(64)
    token_hash = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return raw_token, token_hash, expires_at

def decode_token(token: str) -> dict:
    """Decode and validate a JWT access token"""
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded
    except jwt.PyJWTError:
        return {}
