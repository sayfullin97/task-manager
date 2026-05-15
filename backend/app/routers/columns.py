from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.board import ColumnOut
from app.schemas.column import ColumnCreate, ColumnUpdate
from app.services.auth import get_current_user
from app.services import columns as column_service

router = APIRouter(tags=["columns"])


@router.post("/boards/{board_id}/columns", response_model=ColumnOut, status_code=201)
async def create_column(
    board_id: str,
    data: ColumnCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await column_service.create_column(board_id, data, current_user.id, db)


@router.put("/columns/{column_id}", response_model=ColumnOut)
async def update_column(
    column_id: str,
    data: ColumnUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await column_service.update_column(column_id, data, current_user.id, db)


@router.delete("/columns/{column_id}", status_code=204)
async def delete_column(
    column_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await column_service.delete_column(column_id, current_user.id, db)
