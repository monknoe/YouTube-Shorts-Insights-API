from pydantic import BaseModel
from typing import Optional

class ItemCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class ItemRead(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None

class RequestBody(BaseModel):
    keyword: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    class Config:
        orm_mode = True