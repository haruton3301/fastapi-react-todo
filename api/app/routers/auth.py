from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from psycopg2 import errors as psycopg2_errors

from app.auth import (
    ACCESS_TOKEN_EXPIRES,
    REFRESH_TOKEN_EXPIRES,
    TokenType,
    clear_refresh_cookie,
    create_token,
    get_current_user,
    set_refresh_cookie,
    verify_password,
    verify_token,
)
from app.crud import user as user_crud
from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserResponse, UsernameUpdate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_crud.create_user(db, user_data)
    except psycopg2_errors.UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )


@router.post("/login", response_model=Token)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = user_crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_token(user.id, TokenType.ACCESS, ACCESS_TOKEN_EXPIRES)
    refresh_token = create_token(user.id, TokenType.REFRESH, REFRESH_TOKEN_EXPIRES)
    set_refresh_cookie(response, refresh_token)
    return Token(access_token=access_token)


@router.post("/refresh", response_model=Token)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )
    user_id = verify_token(refresh_token, TokenType.REFRESH)
    new_access_token = create_token(user_id, TokenType.ACCESS, ACCESS_TOKEN_EXPIRES)
    new_refresh_token = create_token(user_id, TokenType.REFRESH, REFRESH_TOKEN_EXPIRES)
    set_refresh_cookie(response, new_refresh_token)
    return Token(access_token=new_access_token)


@router.post("/logout", status_code=204)
def logout(response: Response):
    clear_refresh_cookie(response)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    user_data: UsernameUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return user_crud.update_username(db, current_user, user_data.username)
    except psycopg2_errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Username already taken")
