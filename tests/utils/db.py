import pathlib
from typing import Callable

import alembic.command
import alembic.config
import sqlalchemy as sa
import sqlalchemy.future
from sqlalchemy.ext.asyncio import AsyncConnection


BASE_DIR = [
    p for p in pathlib.Path(__file__).parents if p.parts[-1] == 'tests'
][0].parent
ALEMBIC_INI = BASE_DIR / "alembic.ini"


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
