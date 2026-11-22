"""Local authentication endpoints — register & login with JWT."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.config import get_settings
from app.db.database import get_db
from app.db.models import User
from app.services.auth import create_access_token, hash_password, verify_password
from app.services.demo import DEMO_USER_ID

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    name: str | None = Field(default=None, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    name: str | None


def _auth_response(user: User) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(user.id, user.email),
        user_id=user.id,
        email=user.email,
        name=user.name,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    # Check if email already exists
    existing = db.scalar(select(User).where(User.email == data.email.lower()))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    user = User(
        email=data.email.lower(),
        hashed_password=hash_password(data.password),
        name=data.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(
    data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    return _auth_response(user)


@router.post("/demo-login", response_model=AuthResponse)
def demo_login(
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    settings = get_settings()
    if not settings.demo_mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo login is not enabled.",
        )

    user = db.get(User, DEMO_USER_ID)
    if user is None or user.email != settings.demo_email.strip().lower():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Demo account is not ready. Please try again later.",
        )
    return _auth_response(user)


@router.get("/me")
def get_me(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    db_user = db.scalar(select(User).where(User.id == user["id"]))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"id": db_user.id, "email": db_user.email, "name": db_user.name}
