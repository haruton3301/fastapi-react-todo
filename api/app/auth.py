from datetime import datetime, timedelta, timezone
from enum import StrEnum

import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

pwd_context = PasswordHash((BcryptHasher(),))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

ALGORITHM = "HS256"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"

ACCESS_TOKEN_EXPIRES = timedelta(minutes=settings.access_token_expire_minutes)
REFRESH_TOKEN_EXPIRES = timedelta(days=settings.refresh_token_expire_days)
PASSWORD_RESET_TOKEN_EXPIRES = timedelta(
    minutes=settings.password_reset_token_expire_minutes
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_token(
    user_id: int,
    token_type: TokenType,
    expires_delta: timedelta,
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": str(user_id), "type": token_type, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def verify_token(token: str, expected_type: TokenType) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            raise credentials_exception
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return int(user_id)
    except jwt.InvalidTokenError:
        raise credentials_exception


def create_password_reset_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + PASSWORD_RESET_TOKEN_EXPIRES
    payload = {
        "sub": str(user.id),
        "type": TokenType.PASSWORD_RESET,
        "pwd": user.hashed_password[:8],
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_password_reset_token(token: str) -> tuple[int, str]:
    """(user_id, pwd_fingerprint) を返す。不正なら HTTPException(400)"""
    error = HTTPException(status_code=400, detail="Invalid or expired token")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise error
    if payload.get("type") != TokenType.PASSWORD_RESET:
        raise error
    return int(payload["sub"]), payload.get("pwd", "")


def set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/auth",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/auth",
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    user_id = verify_token(token, TokenType.ACCESS)
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return user
