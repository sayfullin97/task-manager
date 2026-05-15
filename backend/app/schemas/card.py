from typing import List, Optional
from pydantic import BaseModel, model_validator
from app.schemas.auth import UserOut
from app.schemas.board import LabelOut


class CardCreate(BaseModel):
    title: str


class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    cover_color: Optional[str] = None


class MoveCardRequest(BaseModel):
    column_id: str
    position: int


class CommentOut(BaseModel):
    id: str
    text: str
    user: UserOut
    created_at: str

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract(cls, v):
        if hasattr(v, "created_at"):
            return {
                "id": v.id,
                "text": v.text,
                "user": v.user,
                "created_at": v.created_at.isoformat(),
            }
        return v


class CardDetailOut(BaseModel):
    id: str
    column_id: str
    title: str
    description: Optional[str]
    position: int
    due_date: Optional[str]
    cover_color: Optional[str]
    assignees: List[UserOut] = []
    labels: List[LabelOut] = []
    comments: List[CommentOut] = []

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_relations(cls, v):
        if hasattr(v, "assignees"):
            return {
                "id": v.id,
                "column_id": v.column_id,
                "title": v.title,
                "description": v.description,
                "position": v.position,
                "due_date": v.due_date.isoformat() if v.due_date else None,
                "cover_color": v.cover_color,
                "assignees": [a.user for a in v.assignees if hasattr(a, "user")],
                "labels": [cl.label for cl in v.labels if hasattr(cl, "label")],
                "comments": list(v.comments),
            }
        return v


class AssigneeRequest(BaseModel):
    user_id: str


class LabelRequest(BaseModel):
    label_id: str
