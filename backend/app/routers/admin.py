from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.board import Board, BoardMember
from app.models.card import Card
from app.models.column import Column
from app.models.comment import Comment
from app.models.label import Label
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ── Schemas ───────────────────────────────────────────────────────────────────

class AdminUserOut(BaseModel):
    id: str
    name: str
    email: str
    is_admin: bool
    created_at: str
    board_count: int
    model_config = {"from_attributes": True}


class AdminBoardOut(BaseModel):
    id: str
    title: str
    description: str | None
    owner_name: str
    owner_email: str
    member_count: int
    card_count: int
    created_at: str | None = None


class StatsOut(BaseModel):
    users: int
    boards: int
    columns: int
    cards: int
    comments: int
    labels: int


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=StatsOut)
async def get_stats(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return StatsOut(
        users=await db.scalar(select(func.count()).select_from(User)),
        boards=await db.scalar(select(func.count()).select_from(Board)),
        columns=await db.scalar(select(func.count()).select_from(Column)),
        cards=await db.scalar(select(func.count()).select_from(Card)),
        comments=await db.scalar(select(func.count()).select_from(Comment)),
        labels=await db.scalar(select(func.count()).select_from(Label)),
    )


@router.get("/users", response_model=list[AdminUserOut])
async def list_users(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    users = (await db.execute(
        select(User).options(selectinload(User.board_memberships)).order_by(User.created_at)
    )).scalars().all()

    return [
        AdminUserOut(
            id=u.id,
            name=u.name,
            email=u.email,
            is_admin=u.is_admin,
            created_at=u.created_at.strftime("%d.%m.%Y %H:%M"),
            board_count=len(u.board_memberships),
        )
        for u in users
    ]


@router.get("/boards", response_model=list[AdminBoardOut])
async def list_boards(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    boards = (await db.execute(
        select(Board)
        .options(
            selectinload(Board.members).selectinload(BoardMember.user),
            selectinload(Board.columns).selectinload(Column.cards),
        )
        .order_by(Board.title)
    )).scalars().all()

    result = []
    for b in boards:
        owner_member = next((m for m in b.members if m.role == "owner"), None)
        card_count = sum(len(col.cards) for col in b.columns)
        result.append(AdminBoardOut(
            id=b.id,
            title=b.title,
            description=b.description,
            owner_name=owner_member.user.name if owner_member else "—",
            owner_email=owner_member.user.email if owner_member else "—",
            member_count=len(b.members),
            card_count=card_count,
        ))
    return result


@router.patch("/users/{user_id}/toggle-admin", response_model=AdminUserOut)
async def toggle_admin(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own admin status")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = not user.is_admin
    await db.commit()
    await db.refresh(user)
    memberships = (await db.execute(
        select(BoardMember).where(BoardMember.user_id == user_id)
    )).scalars().all()
    return AdminUserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        is_admin=user.is_admin,
        created_at=user.created_at.strftime("%d.%m.%Y %H:%M"),
        board_count=len(memberships),
    )
