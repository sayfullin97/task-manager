from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.board import Board, BoardMember
from app.models.card import Card, CardAssignee, CardLabel
from app.models.column import Column
from app.models.user import User
from app.schemas.board import AddMemberRequest, BoardCreate, BoardUpdate


def _board_options():
    return [
        selectinload(Board.columns).selectinload(Column.cards).selectinload(Card.assignees).selectinload(CardAssignee.user),
        selectinload(Board.columns).selectinload(Column.cards).selectinload(Card.labels).selectinload(CardLabel.label),
        selectinload(Board.members).selectinload(BoardMember.user),
        selectinload(Board.labels),
    ]


async def _get_board_or_404(board_id: str, db: AsyncSession) -> Board:
    board = await db.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


async def _require_member(board_id: str, user_id: str, db: AsyncSession, roles=None) -> BoardMember:
    member = await db.get(BoardMember, (board_id, user_id))
    if not member:
        raise HTTPException(status_code=403, detail="Access denied")
    if roles and member.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return member


async def list_boards(user_id: str, db: AsyncSession) -> List[Board]:
    result = await db.execute(
        select(Board)
        .join(BoardMember, Board.id == BoardMember.board_id)
        .where(BoardMember.user_id == user_id)
    )
    boards = result.scalars().all()

    members = await db.execute(
        select(BoardMember).where(BoardMember.user_id == user_id)
    )
    role_map = {m.board_id: m.role for m in members.scalars().all()}

    for board in boards:
        board.role = role_map.get(board.id)
    return boards


async def create_board(data: BoardCreate, user_id: str, db: AsyncSession) -> Board:
    board = Board(title=data.title, description=data.description, owner_id=user_id)
    db.add(board)
    await db.flush()

    member = BoardMember(board_id=board.id, user_id=user_id, role="owner")
    db.add(member)
    await db.commit()
    await db.refresh(board)
    board.role = "owner"
    return board


async def get_board(board_id: str, user_id: str, db: AsyncSession) -> Board:
    await _require_member(board_id, user_id, db)

    result = await db.execute(
        select(Board)
        .options(*_board_options())
        .where(Board.id == board_id)
    )
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


async def update_board(board_id: str, data: BoardUpdate, user_id: str, db: AsyncSession) -> Board:
    await _require_member(board_id, user_id, db, roles=["owner", "member"])
    board = await _get_board_or_404(board_id, db)

    if data.title is not None:
        board.title = data.title
    if data.description is not None:
        board.description = data.description

    await db.commit()
    await db.refresh(board)
    return board


async def delete_board(board_id: str, user_id: str, db: AsyncSession) -> None:
    await _require_member(board_id, user_id, db, roles=["owner"])
    board = await _get_board_or_404(board_id, db)
    await db.delete(board)
    await db.commit()


async def list_members(board_id: str, user_id: str, db: AsyncSession) -> List[BoardMember]:
    await _require_member(board_id, user_id, db)
    result = await db.execute(
        select(BoardMember)
        .options(selectinload(BoardMember.user))
        .where(BoardMember.board_id == board_id)
    )
    return result.scalars().all()


async def add_member(board_id: str, data: AddMemberRequest, user_id: str, db: AsyncSession) -> BoardMember:
    await _require_member(board_id, user_id, db, roles=["owner"])

    user = await db.scalar(select(User).where(User.email == data.email))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = await db.get(BoardMember, (board_id, user.id))
    if existing:
        raise HTTPException(status_code=400, detail="User already a member")

    member = BoardMember(board_id=board_id, user_id=user.id, role=data.role)
    db.add(member)
    await db.commit()

    result = await db.execute(
        select(BoardMember)
        .options(selectinload(BoardMember.user))
        .where(BoardMember.board_id == board_id, BoardMember.user_id == user.id)
    )
    return result.scalar_one()


async def remove_member(board_id: str, target_user_id: str, user_id: str, db: AsyncSession) -> None:
    await _require_member(board_id, user_id, db, roles=["owner"])
    member = await db.get(BoardMember, (board_id, target_user_id))
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if member.role == "owner":
        raise HTTPException(status_code=400, detail="Cannot remove board owner")
    await db.delete(member)
    await db.commit()
