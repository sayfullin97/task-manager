from typing import Optional
from pydantic import BaseModel


class ColumnCreate(BaseModel):
    title: str


class ColumnUpdate(BaseModel):
    title: Optional[str] = None
    position: Optional[int] = None
