import asyncio
import pathlib
from typing import Callable

import alembic.command
import alembic.config
import pytest
import pytest_asyncio
import sqlalchemy as sa
import sqlalchemy.event
import sqlalchemy.future
import sqlalchemy.pool
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ansible_events_ui.app import setup_cors, setup_routes
from ansible_events_ui.config import load_settings
from ansible_events_ui.db.session import get_db_session, get_db_sessionmaker

BASE_DIR = pathlib.Path(__file__).parents[2]
ALEMBIC_INI = BASE_DIR / "alembic.ini"


def alembic_command_wrapper(
    connection: sqlalchemy.future.Engine,
    command: Callable[[alembic.config.Config, ...], None],
    config: alembic.config.Config,
    *args,
    **kwargs,
):
    config.attributes["connection"] = connection
    command(config, *args, **kwargs)


def create_test_app(settings, session):
    app = FastAPI(title="Ansible Events API")
    app.state.settings = settings

    setup_cors(app)
    setup_routes(app)

    app.dependency_overrides.update(
        {
            get_db_session: lambda: session,
            get_db_sessionmaker: lambda: lambda: session,
        }
    )

    return app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def default_settings():
    return load_settings()


@pytest_asyncio.fixture(scope="session")
async def default_engine(default_settings):
    engine = create_async_engine(
        default_settings.database_url,
        isolation_level="AUTOCOMMIT",
        poolclass=sqlalchemy.pool.NullPool,
        future=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def db_url(default_settings):
    default_url = sqlalchemy.engine.make_url(default_settings.database_url)
    return default_url.set(database=f"test_{default_url.database}")


@pytest_asyncio.fixture(scope="session")
async def db_engine(default_engine, db_url):
    async with default_engine.connect() as connection:
        query = f'DROP DATABASE IF EXISTS "{db_url.database}"'
        await connection.execute(sa.text(query))
        query = f'CREATE DATABASE "{db_url.database}"'
        await connection.execute(sa.text(query))

    engine = create_async_engine(
        db_url,
        poolclass=sqlalchemy.pool.NullPool,
        future=True,
    )

    async with engine.connect() as connection:
        await connection.run_sync(
            alembic_command_wrapper,
            alembic.command.upgrade,
            alembic.config.Config(str(ALEMBIC_INI)),
            "head",
        )

    yield engine

    await engine.dispose()

    async with default_engine.connect() as connection:
        query = f'DROP DATABASE IF EXISTS "{db_url.database}"'
        await connection.execute(sa.text(query))


@pytest_asyncio.fixture
async def db(db_engine):
    session_factory = sessionmaker(class_=AsyncSession, expire_on_commit=True)

    async with db_engine.connect() as connection:
        transaction = await connection.begin()
        await connection.begin_nested()

        async with session_factory(bind=connection) as session:

            @sqlalchemy.event.listens_for(
                session.sync_session, "after_transaction_end"
            )
            def reopen_nested_transaction(_session, _transaction):
                if connection.closed:
                    return

                if not connection.in_nested_transaction():
                    connection.sync_connection.begin_nested()

            yield session

            await transaction.rollback()


@pytest.fixture
def app(default_settings, db, db_url):
    settings = default_settings.copy(update={"database_url": db_url})
    return create_test_app(settings, db)


@pytest_asyncio.fixture
async def client(app: FastAPI):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
