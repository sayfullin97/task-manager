from typing import List, Optional
from pydantic import BaseModel, model_validator
from app.schemas.auth import UserOut


class BoardCreate(BaseModel):
    title: str
    description: Optional[str] = None


class BoardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class MemberOut(BaseModel):
    user: UserOut
    role: str

    model_config = {"from_attributes": True}


class LabelOut(BaseModel):
    id: str
    name: str
    color: str

    model_config = {"from_attributes": True}


class CardBriefOut(BaseModel):
    id: str
    title: str
    position: int
    due_date: Optional[str] = None
    cover_color: Optional[str] = None
    assignees: List[UserOut] = []
    labels: List[LabelOut] = []

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_relations(cls, v):
        if hasattr(v, "assignees"):
            assignees = [a.user for a in v.assignees if hasattr(a, "user")]
            labels = [cl.label for cl in v.labels if hasattr(cl, "label")]
            due = v.due_date.isoformat() if v.due_date else None
            return {
                "id": v.id,
                "title": v.title,
                "position": v.position,
                "due_date": due,
                "cover_color": v.cover_color,
                "assignees": assignees,
                "labels": labels,
            }
        return v


class ColumnOut(BaseModel):
    id: str
    title: str
    position: int
    cards: List[CardBriefOut] = []

    model_config = {"from_attributes": True}


class BoardOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    owner_id: str
    role: Optional[str] = None

    model_config = {"from_attributes": True}


class BoardDetailOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    owner_id: str
    columns: List[ColumnOut] = []
    members: List[MemberOut] = []
    labels: List[LabelOut] = []

    model_config = {"from_attributes": True}


class AddMemberRequest(BaseModel):
    email: str
    role: str = "member"
