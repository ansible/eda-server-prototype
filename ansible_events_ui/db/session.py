from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ansible_events_ui.config import settings
from ansible_events_ui.db.models import User

# TODO(cutwater): Do not initialize engine globally
async_engine = create_async_engine(settings.database_url)
# TODO(cutwater): After migration to SQLAlchemy 2.0 style is complete,
#   add `future=True` argument to the `sessionmaker(...)` call.
async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    # future=True,  # noqa: E800
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_db_session)):
    yield SQLAlchemyUserDatabase(session, User)
