from pydantic import BaseModel


class BookContract(BaseModel):
    id: int
    title: str
    available_copies: int

    @property
    def is_available(self) -> bool:
        return self.available_copies > 0