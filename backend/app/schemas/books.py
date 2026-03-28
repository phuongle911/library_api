from pydantic import BaseModel, Field, ConfigDict

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    author: str = Field(..., min_length=1, max_length=255)
    category_id: int


class BookCreate(BookBase):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    author: str = Field(..., min_length=1, max_length=255)
    category_id: int


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    author: str | None = Field(default=None, min_length=1, max_length=255)
    category_id: int | None = None


class CategoryMiniResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    title: str
    author: str
    description: str | None
    category_id: int


class BookListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    author: str
    owner_id: int
    category_id: int
    category: CategoryMiniResponse
    
        
