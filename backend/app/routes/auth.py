"""
Authentication routes.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from ..config import settings
from ..services.auth_service import AuthService
from ..models.user import RegisterRequest, LoginRequest
from ..models.token import Token

router = APIRouter()


@router.post("/register", response_model=dict)
def register(register_in: RegisterRequest):
    return AuthService.register_user(
        name=register_in.name,
        email=str(register_in.email),
        password=register_in.password,
        role=register_in.role,
    )


@router.post("/login", response_model=Token)
def login(login_in: LoginRequest):
    return AuthService.login_user(login_in)
