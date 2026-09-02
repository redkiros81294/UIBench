"""
User models.
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uuid


class UserModel(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    hashed_password: str
    role: str = "user"


class UserInDB(UserModel):
    projects: List[str] = []


class UserResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    role: str
    projects: List[str] = []


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "user"
