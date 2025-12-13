from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    #password: str


class UserCreate(UserBase):
    password: str | None = Field(None, min_length=6, max_length=80)


class UserUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str | None = Field(None, min_length=6, max_length=80)


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str | None = Field(None, min_length=6, max_length=80)
