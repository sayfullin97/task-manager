from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.boards import router as boards_router
from app.routers.columns import router as columns_router
from app.routers.cards import router as cards_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Task Manager API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"
app.include_router(auth_router, prefix=PREFIX)
app.include_router(boards_router, prefix=PREFIX)
app.include_router(columns_router, prefix=PREFIX)
app.include_router(cards_router, prefix=PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok"}
