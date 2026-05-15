from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserOut
from app.services.auth import get_current_user, login, refresh, register
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register_route(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register(data, db)


@router.post("/login", response_model=TokenResponse)
async def login_route(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login(data, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_route(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await refresh(data.refresh_token, db)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
