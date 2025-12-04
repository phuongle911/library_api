from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    # password: str = Field(..., min_length=6, max_length=80)
    pass


class UserUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr


class UserResponse(UserBase):
    id: int


    class Config:
        orm_mode = True