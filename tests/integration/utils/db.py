#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pathlib
from typing import Callable

import alembic.command
import alembic.config
import sqlalchemy as sa
import sqlalchemy.future
from sqlalchemy.ext.asyncio import AsyncConnection

BASE_DIR = pathlib.Path(__file__).parents[3]
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
