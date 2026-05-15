from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.card import (
    AssigneeRequest,
    CardCreate,
    CardDetailOut,
    CardUpdate,
    CommentOut,
    LabelRequest,
    MoveCardRequest,
)
from app.schemas.comment import CommentCreate, CommentUpdate
from app.services.auth import get_current_user
from app.services import cards as card_service

router = APIRouter(tags=["cards"])


@router.post("/columns/{column_id}/cards", response_model=CardDetailOut, status_code=201)
async def create_card(
    column_id: str,
    data: CardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    card = await card_service.create_card(column_id, data, current_user.id, db)
    return await card_service.get_card(card.id, current_user.id, db)


@router.get("/cards/{card_id}", response_model=CardDetailOut)
async def get_card(
    card_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await card_service.get_card(card_id, current_user.id, db)


@router.put("/cards/{card_id}", response_model=CardDetailOut)
async def update_card(
    card_id: str,
    data: CardUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await card_service.update_card(card_id, data, current_user.id, db)
    return await card_service.get_card(card_id, current_user.id, db)


@router.delete("/cards/{card_id}", status_code=204)
async def delete_card(
    card_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await card_service.delete_card(card_id, current_user.id, db)


@router.post("/cards/{card_id}/move", response_model=CardDetailOut)
async def move_card(
    card_id: str,
    data: MoveCardRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await card_service.move_card(card_id, data, current_user.id, db)
    return await card_service.get_card(card_id, current_user.id, db)


@router.post("/cards/{card_id}/assignees", response_model=CardDetailOut)
async def add_assignee(
    card_id: str,
    data: AssigneeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await card_service.add_assignee(card_id, data.user_id, current_user.id, db)


@router.delete("/cards/{card_id}/assignees/{user_id}", status_code=204)
async def remove_assignee(
    card_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await card_service.remove_assignee(card_id, user_id, current_user.id, db)


@router.post("/cards/{card_id}/labels", response_model=CardDetailOut)
async def add_label(
    card_id: str,
    data: LabelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await card_service.add_label(card_id, data.label_id, current_user.id, db)


@router.delete("/cards/{card_id}/labels/{label_id}", status_code=204)
async def remove_label(
    card_id: str,
    label_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await card_service.remove_label(card_id, label_id, current_user.id, db)


@router.post("/cards/{card_id}/comments", response_model=CommentOut, status_code=201)
async def add_comment(
    card_id: str,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await card_service.add_comment(card_id, data.text, current_user.id, db)


@router.put("/comments/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id: str,
    data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await card_service.update_comment(comment_id, data.text, current_user.id, db)


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await card_service.delete_comment(comment_id, current_user.id, db)


@router.put("/labels/{label_id}")
async def update_label(
    label_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.schemas.label import LabelUpdate
    from app.services import labels as label_service
    pass


@router.delete("/labels/{label_id}", status_code=204)
async def delete_label(
    label_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.services import labels as label_service
    await label_service.delete_label(label_id, current_user.id, db)
