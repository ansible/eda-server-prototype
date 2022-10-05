from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from eda_server.config import Settings


def engine_from_config(config: Settings, **kwargs) -> AsyncEngine:
    return create_async_engine(url=config.database_url, **kwargs)


def create_session_factory(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
