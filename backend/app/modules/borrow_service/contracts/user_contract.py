from pydantic import BaseModel


class UserContract(BaseModel):
    id: int
    email: str
    is_active: bool = True
