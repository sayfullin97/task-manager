from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.board import BoardMember
from app.models.card import Card, CardAssignee, CardLabel
from app.models.column import Column
from app.schemas.column import ColumnCreate, ColumnUpdate


async def _load_column(column_id: str, db: AsyncSession) -> Column:
    result = await db.execute(
        select(Column)
        .options(
            selectinload(Column.cards).selectinload(Card.assignees).selectinload(CardAssignee.user),
            selectinload(Column.cards).selectinload(Card.labels).selectinload(CardLabel.label),
        )
        .where(Column.id == column_id)
    )
    return result.scalar_one()


async def _require_board_member(board_id: str, user_id: str, db: AsyncSession, roles=None):
    member = await db.get(BoardMember, (board_id, user_id))
    if not member:
        raise HTTPException(status_code=403, detail="Access denied")
    if roles and member.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")


async def _next_position(board_id: str, db: AsyncSession) -> int:
    result = await db.execute(
        select(Column.position)
        .where(Column.board_id == board_id)
        .order_by(Column.position.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    return (last + 1000) if last else 1000


async def create_column(board_id: str, data: ColumnCreate, user_id: str, db: AsyncSession) -> Column:
    await _require_board_member(board_id, user_id, db, roles=["owner", "member"])
    position = await _next_position(board_id, db)
    column = Column(board_id=board_id, title=data.title, position=position)
    db.add(column)
    await db.commit()
    return await _load_column(column.id, db)


async def update_column(column_id: str, data: ColumnUpdate, user_id: str, db: AsyncSession) -> Column:
    column = await db.get(Column, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    await _require_board_member(column.board_id, user_id, db, roles=["owner", "member"])

    if data.title is not None:
        column.title = data.title
    if data.position is not None:
        column.position = data.position

    await db.commit()
    return await _load_column(column_id, db)


async def delete_column(column_id: str, user_id: str, db: AsyncSession) -> None:
    column = await db.get(Column, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    await _require_board_member(column.board_id, user_id, db, roles=["owner", "member"])
    await db.delete(column)
    await db.commit()
