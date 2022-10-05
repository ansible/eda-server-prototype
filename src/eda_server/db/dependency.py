from typing import AsyncGenerator

import sqlalchemy.orm
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_db_session_factory() -> sqlalchemy.orm.sessionmaker:
    """Database sessionmaker dependency stub."""
    raise NotImplementedError


async def get_db_session(
    session_factory: sqlalchemy.orm.sessionmaker = Depends(
        get_db_session_factory
    ),
) -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency."""
    async with session_factory() as session:
        yield session
