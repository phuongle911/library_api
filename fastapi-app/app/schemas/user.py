from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# class UserBase(BaseModel):
#     name: str = Field(..., min_length=2, max_length=50)
#     email: EmailStr
#     #password: str


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

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str | None = Field(None, min_length=6, max_length=80)
