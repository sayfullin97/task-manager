from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.board import (
    AddMemberRequest,
    BoardCreate,
    BoardDetailOut,
    BoardOut,
    BoardUpdate,
    MemberOut,
    LabelOut,
)
from app.schemas.label import LabelCreate, LabelUpdate
from app.services.auth import get_current_user
from app.services import boards as board_service
from app.services import labels as label_service

router = APIRouter(prefix="/boards", tags=["boards"])


@router.get("", response_model=List[BoardOut])
async def list_boards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await board_service.list_boards(current_user.id, db)


@router.post("", response_model=BoardOut, status_code=201)
async def create_board(
    data: BoardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await board_service.create_board(data, current_user.id, db)


@router.get("/{board_id}", response_model=BoardDetailOut)
async def get_board(
    board_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await board_service.get_board(board_id, current_user.id, db)


@router.put("/{board_id}", response_model=BoardOut)
async def update_board(
    board_id: str,
    data: BoardUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await board_service.update_board(board_id, data, current_user.id, db)


@router.delete("/{board_id}", status_code=204)
async def delete_board(
    board_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await board_service.delete_board(board_id, current_user.id, db)


@router.get("/{board_id}/members", response_model=List[MemberOut])
async def list_members(
    board_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await board_service.list_members(board_id, current_user.id, db)


@router.post("/{board_id}/members", response_model=MemberOut, status_code=201)
async def add_member(
    board_id: str,
    data: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await board_service.add_member(board_id, data, current_user.id, db)


@router.delete("/{board_id}/members/{user_id}", status_code=204)
async def remove_member(
    board_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await board_service.remove_member(board_id, user_id, current_user.id, db)


@router.get("/{board_id}/labels", response_model=List[LabelOut])
async def list_labels(
    board_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await label_service.list_labels(board_id, current_user.id, db)


@router.post("/{board_id}/labels", response_model=LabelOut, status_code=201)
async def create_label(
    board_id: str,
    data: LabelCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await label_service.create_label(board_id, data, current_user.id, db)
