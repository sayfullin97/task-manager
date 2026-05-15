from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import BoardMember
from app.models.label import Label
from app.schemas.label import LabelCreate, LabelUpdate


async def _require_member(board_id: str, user_id: str, db: AsyncSession, roles=None):
    member = await db.get(BoardMember, (board_id, user_id))
    if not member:
        raise HTTPException(status_code=403, detail="Access denied")
    if roles and member.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")


async def list_labels(board_id: str, user_id: str, db: AsyncSession):
    await _require_member(board_id, user_id, db)
    result = await db.execute(select(Label).where(Label.board_id == board_id))
    return result.scalars().all()


async def create_label(board_id: str, data: LabelCreate, user_id: str, db: AsyncSession) -> Label:
    await _require_member(board_id, user_id, db, roles=["owner", "member"])
    label = Label(board_id=board_id, name=data.name, color=data.color)
    db.add(label)
    await db.commit()
    await db.refresh(label)
    return label


async def update_label(label_id: str, data: LabelUpdate, user_id: str, db: AsyncSession) -> Label:
    label = await db.get(Label, label_id)
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    await _require_member(label.board_id, user_id, db, roles=["owner", "member"])

    if data.name is not None:
        label.name = data.name
    if data.color is not None:
        label.color = data.color

    await db.commit()
    await db.refresh(label)
    return label


async def delete_label(label_id: str, user_id: str, db: AsyncSession) -> None:
    label = await db.get(Label, label_id)
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    await _require_member(label.board_id, user_id, db, roles=["owner", "member"])
    await db.delete(label)
    await db.commit()
