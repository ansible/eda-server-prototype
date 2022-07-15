from typing import AsyncGenerator

import sqlalchemy
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings
from .models import User, metadata

engine = sqlalchemy.create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)
# FIXME(cutwater): Do not create database schema at the module load time.
metadata.create_all(engine)

# TODO(cutwater): Do not initialize engine globally
async_engine = create_async_engine(settings.async_database_url)
# TODO(cutwater): After migration to SQLAlchemy 2.0 style is complete,
#   add `future=True` argument to the `sessionmaker(...)` call.
async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    # future=True,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
