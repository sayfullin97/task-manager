from typing import Optional
from pydantic import BaseModel


class LabelCreate(BaseModel):
    name: str
    color: str = "#6b7280"


class LabelUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
