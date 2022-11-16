import asyncio

import pytest
import pytest_asyncio
import sqlalchemy.event
import sqlalchemy.future
import sqlalchemy.pool
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from eda_server.config import load_settings

from .utils.app import create_test_app
from .utils.db import create_database, drop_database, upgrade_database


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
        await create_database(connection, db_url.database)

    engine = create_async_engine(
        db_url,
        poolclass=sqlalchemy.pool.NullPool,
        future=True,
    )

    async with engine.connect() as connection:
        await upgrade_database(connection)

    yield engine

    await engine.dispose()

    async with default_engine.connect() as connection:
        await drop_database(connection, db_url.database)


@pytest_asyncio.fixture
async def db(db_engine):
    session_factory = sessionmaker(class_=AsyncSession, expire_on_commit=False)

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


@pytest_asyncio.fixture
async def app(default_settings, db, db_url):
    settings = default_settings.copy(update={"database_url": db_url})
    return await create_test_app(settings, db)


@pytest_asyncio.fixture
async def client(app: FastAPI):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
