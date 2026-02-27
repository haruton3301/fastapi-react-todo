from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from psycopg2 import errors as psycopg2_errors

from app.auth import (
    ACCESS_TOKEN_EXPIRES,
    PASSWORD_RESET_TOKEN_EXPIRES,
    REFRESH_TOKEN_EXPIRES,
    TokenType,
    clear_refresh_cookie,
    create_token,
    get_current_user_id,
    set_refresh_cookie,
    verify_password,
    verify_token,
)
from app.crud import user as user_crud
from app.database import get_db
from app.email import send_password_reset_email
from app.models.user import User
from app.schemas.auth import (
    LoginResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
    UserCreate,
    UserResponse,
    UsernameUpdate,
)

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


@router.post("/login", response_model=LoginResponse)
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
    return LoginResponse(
        token=Token(access_token=access_token),
        user=user,
    )


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
def get_me(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


@router.put("/me", response_model=UserResponse)
def update_me(
    user_data: UsernameUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        return user_crud.update_username(db, user, user_data.username)
    except psycopg2_errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Username already taken")


@router.post("/password-reset/request", status_code=202)
def request_password_reset(
    data: PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    user = user_crud.get_user_by_email(db, data.email)
    if user:
        token = create_token(user.id, TokenType.PASSWORD_RESET, PASSWORD_RESET_TOKEN_EXPIRES)
        background_tasks.add_task(send_password_reset_email, user.email, token)
    return Response(status_code=202)


@router.post("/password-reset/confirm")
def confirm_password_reset(
    data: PasswordResetConfirm, db: Session = Depends(get_db)
):
    user_id = verify_token(data.token, TokenType.PASSWORD_RESET)
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user_crud.update_password(db, user, data.new_password)
    return {"message": "Password reset successful"}
