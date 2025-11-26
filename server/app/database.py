import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.models import Base

# Prefer env; fallback only for local dev.
DATABASE_URL = os.getenv("DATABASE_URL", get_settings().database_url)

engine = create_async_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup and dispose engine on shutdown."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        await engine.dispose()
