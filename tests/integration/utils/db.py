import pathlib
from typing import Callable

import alembic.command
import alembic.config
import sqlalchemy as sa
import sqlalchemy.future
from sqlalchemy.ext.asyncio import AsyncConnection

from eda_server.db import models

BASE_DIR = pathlib.Path(__file__).parents[3]
ALEMBIC_INI = BASE_DIR / "alembic.ini"

ADMIN_USER_EMAIL = "admin@example.com"


async def drop_database(connection: AsyncConnection, name: str):
    await connection.execute(sa.text(f'DROP DATABASE IF EXISTS "{name}"'))


async def create_database(connection: AsyncConnection, name: str):
    await drop_database(connection, name)
    await connection.execute(sa.text(f'CREATE DATABASE "{name}"'))


def alembic_command_wrapper(
    connection: sqlalchemy.future.Engine,
    command: Callable[[alembic.config.Config, ...], None],
    config: alembic.config.Config,
    *args,
    **kwargs,
):
    config.attributes["connection"] = connection
    command(config, *args, **kwargs)


async def upgrade_database(connection):
    await connection.run_sync(
        alembic_command_wrapper,
        alembic.command.upgrade,
        alembic.config.Config(str(ALEMBIC_INI)),
        "head",
    )


async def insert_initial_data(connection):
    await connection.execute(
        sa.insert(models.User).values(
            email=ADMIN_USER_EMAIL,
            is_active=True,
            is_superuser=True,
            hashed_password="",
        )
    )
    await connection.commit()


async def get_admin_user(connection):
    return (
        await connection.scalars(
            sa.select(models.User).filter_by(email=ADMIN_USER_EMAIL)
        )
    ).one()
