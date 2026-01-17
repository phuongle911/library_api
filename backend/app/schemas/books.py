from pydantic import BaseModel, Field, validator

class BookBase(BaseModel):
    title: str = Field(..., min_length=2, max_lenght=50)
    description: str = Field(..., min_length=2, max_lenght=200)
    author: str = Field(..., min_length=2, max_lenght=20)


class BookCreate(BookBase):
    title: str #= Field(..., min_length=2, max_lenght=50)
    description: str = Field(..., min_length=2, max_lenght=200)
    author: str = Field(..., min_length=2, max_lenght=20)
    @validator("title")
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Title can not be blank")
        return v



class BookUpdate(BaseModel):
    title: str = Field(..., min_length=2, max_lenght=50)
    description: str = Field(..., min_length=2, max_lenght=200)
    author: str = Field(..., min_length=2, max_lenght=20)

class BookResponse(BookBase):
    id: int


    class Config:
        orm_mode = True
        
