from typing import AsyncGenerator

import databases
import sqlalchemy
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .models import User, metadata
from .conf import env

DATABASE_URL = env.str("DATABASE_URL", default="sqlite:///./test.db")
ASYNC_DATABASE_URL = env.str(
    "ASYNC_DATABASE_URL", default="sqlite+aiosqlite:///./test.db"
)

database = databases.Database(DATABASE_URL)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

async_engine = create_async_engine(ASYNC_DATABASE_URL)
async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
