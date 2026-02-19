from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    clear_refresh_cookie,
    create_access_token,
    create_refresh_token,
    get_current_user,
    set_refresh_cookie,
    verify_password,
    verify_refresh_token,
)
from app.crud import auth as auth_crud
from app.crud.auth import DuplicateUserError
from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        return auth_crud.create_user(db, user_data)
    except DuplicateUserError:
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
    user = auth_crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(user.id)
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
    user_id = verify_refresh_token(refresh_token)
    new_access_token = create_access_token(data={"sub": str(user_id)})
    new_refresh_token = create_refresh_token(user_id)
    set_refresh_cookie(response, new_refresh_token)
    return Token(access_token=new_access_token)


@router.post("/logout", status_code=204)
def logout(response: Response):
    clear_refresh_cookie(response)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
