from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.board import BoardMember
from app.models.card import Card, CardAssignee, CardLabel
from app.models.column import Column
from app.models.comment import Comment
from app.models.label import Label
from app.models.user import User
from app.schemas.card import CardCreate, CardUpdate, MoveCardRequest


def _card_options():
    return [
        selectinload(Card.assignees).selectinload(CardAssignee.user),
        selectinload(Card.labels).selectinload(CardLabel.label),
        selectinload(Card.comments).selectinload(Comment.user),
    ]


async def _get_card_or_404(card_id: str, db: AsyncSession) -> Card:
    card = await db.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


async def _get_board_id_for_column(column_id: str, db: AsyncSession) -> str:
    column = await db.get(Column, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return column.board_id


async def _require_member(board_id: str, user_id: str, db: AsyncSession, roles=None):
    member = await db.get(BoardMember, (board_id, user_id))
    if not member:
        raise HTTPException(status_code=403, detail="Access denied")
    if roles and member.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")


async def _next_position(column_id: str, db: AsyncSession) -> int:
    result = await db.execute(
        select(Card.position)
        .where(Card.column_id == column_id)
        .order_by(Card.position.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    return (last + 1000) if last else 1000


async def create_card(column_id: str, data: CardCreate, user_id: str, db: AsyncSession) -> Card:
    board_id = await _get_board_id_for_column(column_id, db)
    await _require_member(board_id, user_id, db, roles=["owner", "member"])
    position = await _next_position(column_id, db)
    card = Card(column_id=column_id, title=data.title, position=position)
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card


async def get_card(card_id: str, user_id: str, db: AsyncSession) -> Card:
    simple = await _get_card_or_404(card_id, db)
    board_id = await _get_board_id_for_column(simple.column_id, db)
    await _require_member(board_id, user_id, db)

    result = await db.execute(
        select(Card).options(*_card_options()).where(Card.id == card_id)
    )
    return result.scalar_one()


async def update_card(card_id: str, data: CardUpdate, user_id: str, db: AsyncSession) -> Card:
    card = await _get_card_or_404(card_id, db)
    board_id = await _get_board_id_for_column(card.column_id, db)
    await _require_member(board_id, user_id, db, roles=["owner", "member"])

    if data.title is not None:
        card.title = data.title
    if data.description is not None:
        card.description = data.description
    if data.cover_color is not None:
        card.cover_color = data.cover_color
    if data.due_date is not None:
        card.due_date = datetime.fromisoformat(data.due_date)

    await db.commit()
    await db.refresh(card)
    return card


async def delete_card(card_id: str, user_id: str, db: AsyncSession) -> None:
    card = await _get_card_or_404(card_id, db)
    board_id = await _get_board_id_for_column(card.column_id, db)
    await _require_member(board_id, user_id, db, roles=["owner", "member"])
    await db.delete(card)
    await db.commit()


async def move_card(card_id: str, data: MoveCardRequest, user_id: str, db: AsyncSession) -> Card:
    card = await _get_card_or_404(card_id, db)
    board_id = await _get_board_id_for_column(card.column_id, db)
    await _require_member(board_id, user_id, db, roles=["owner", "member"])

    target_board_id = await _get_board_id_for_column(data.column_id, db)
    if target_board_id != board_id:
        raise HTTPException(status_code=400, detail="Cannot move card to another board")

    card.column_id = data.column_id
    card.position = data.position
    await db.commit()
    await db.refresh(card)
    return card


async def add_assignee(card_id: str, target_user_id: str, user_id: str, db: AsyncSession) -> Card:
    card = await _get_card_or_404(card_id, db)
    board_id = await _get_board_id_for_column(card.column_id, db)
    await _require_member(board_id, user_id, db, roles=["owner", "member"])

    user = await db.get(User, target_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = await db.get(CardAssignee, (card_id, target_user_id))
    if not existing:
        db.add(CardAssignee(card_id=card_id, user_id=target_user_id))
        await db.commit()

    return await get_card(card_id, user_id, db)


async def remove_assignee(card_id: str, target_user_id: str, user_id: str, db: AsyncSession) -> None:
    card = await _get_card_or_404(card_id, db)
    board_id = await _get_board_id_for_column(card.column_id, db)
    await _require_member(board_id, user_id, db, roles=["owner", "member"])

    assignee = await db.get(CardAssignee, (card_id, target_user_id))
    if assignee:
        await db.delete(assignee)
        await db.commit()


async def add_label(card_id: str, label_id: str, user_id: str, db: AsyncSession) -> Card:
    card = await _get_card_or_404(card_id, db)
    board_id = await _get_board_id_for_column(card.column_id, db)
    await _require_member(board_id, user_id, db, roles=["owner", "member"])

    label = await db.get(Label, label_id)
    if not label or label.board_id != board_id:
        raise HTTPException(status_code=404, detail="Label not found")

    existing = await db.get(CardLabel, (card_id, label_id))
    if not existing:
        db.add(CardLabel(card_id=card_id, label_id=label_id))
        await db.commit()

    return await get_card(card_id, user_id, db)


async def remove_label(card_id: str, label_id: str, user_id: str, db: AsyncSession) -> None:
    card = await _get_card_or_404(card_id, db)
    board_id = await _get_board_id_for_column(card.column_id, db)
    await _require_member(board_id, user_id, db, roles=["owner", "member"])

    card_label = await db.get(CardLabel, (card_id, label_id))
    if card_label:
        await db.delete(card_label)
        await db.commit()


async def add_comment(card_id: str, text: str, user_id: str, db: AsyncSession) -> Comment:
    card = await _get_card_or_404(card_id, db)
    board_id = await _get_board_id_for_column(card.column_id, db)
    await _require_member(board_id, user_id, db)

    comment = Comment(card_id=card_id, user_id=user_id, text=text)
    db.add(comment)
    await db.commit()

    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.id == comment.id)
    )
    return result.scalar_one()


async def update_comment(comment_id: str, text: str, user_id: str, db: AsyncSession) -> Comment:
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only edit own comments")
    comment.text = text
    await db.commit()

    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.id == comment_id)
    )
    return result.scalar_one()


async def delete_comment(comment_id: str, user_id: str, db: AsyncSession) -> None:
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only delete own comments")
    await db.delete(comment)
    await db.commit()
