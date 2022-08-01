from typing import AsyncGenerator

from fastapi import Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker as SessionMaker  # noqa: N812

from ansible_events_ui.config import Settings


def engine_from_settings(settings: Settings) -> AsyncEngine:
    return create_async_engine(settings.database_url)


def create_sessionmaker(engine: AsyncEngine) -> SessionMaker:
    # TODO(cutwater): After migration to SQLAlchemy 2.0 style is complete,
    #   add `future=True` argument to the `sessionmaker(...)` call.
    return SessionMaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        # future=True,  # noqa: E800
    )


# TODO(cutwater): Move dependencies into standalone package
def get_db_sessionmaker(request: Request) -> SessionMaker:
    """Database sessionmaker dependency."""
    return request.app.state.db_sessionmaker


# TODO(cutwater): Move dependencies into standalone package
async def get_db_session(
    sessionmaker: SessionMaker = Depends(get_db_sessionmaker),
) -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency."""
    async with sessionmaker() as session:
        yield session
