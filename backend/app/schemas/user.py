from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    user = "user"

    
class UserCreate(BaseModel):
    password: str | None = Field(None, min_length=6, max_length=80)
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr


class UserUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str | None = Field(None, min_length=6, max_length=80)


class UserResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: EmailStr
    role: UserRole = UserRole.user

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str | None = Field(None, min_length=6, max_length=80)


class RefreshTokenSchema(BaseModel):
    refresh_token: str


