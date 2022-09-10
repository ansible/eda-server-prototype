import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from ansible_events_ui.config import Settings

__all__ = (
    "Engine",
    "Session",
    "SessionFactory",
    "engine_from_config",
    "create_engine",
    "create_session_factory",
)

# Type and function aliases
SessionFactory = sqlalchemy.orm.sessionmaker
Engine = sqlalchemy.ext.asyncio.AsyncEngine
Session = sqlalchemy.ext.asyncio.AsyncSession
create_engine = sqlalchemy.ext.asyncio.create_async_engine


def engine_from_config(config: Settings, **kwargs) -> Engine:
    return create_engine(url=config.database_url, **kwargs)


def create_session_factory(engine: Engine) -> SessionFactory:
    return SessionFactory(bind=engine, class_=Session, expire_on_commit=False)
