from typing import AsyncGenerator

import databases
import sqlalchemy
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings
from .models import User, metadata

database = databases.Database(settings.database_url)

engine = sqlalchemy.create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

async_engine = create_async_engine(settings.async_database_url)
async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
