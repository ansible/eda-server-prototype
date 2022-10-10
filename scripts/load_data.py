#!/usr/bin/env python
# TODO(cutwater): Move to eda_server.cli package
# TODO(cutwater): Add integration tests for this script
import argparse
import asyncio
import itertools
import logging
import sys
from typing import List

import pydantic
import sqlalchemy as sa
import yaml
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server import schema
from eda_server.config import load_settings
from eda_server.db import models
from eda_server.db.session import (
    create_session_factory,
    dispose_context,
    engine_from_config,
)
from eda_server.types import Action, ResourceType
from eda_server.users import UserManager, get_user_db, get_user_manager

logger = logging.getLogger()


EXIT_SUCCESS = 0
EXIT_ERROR = 1


class ApplicationError(Exception):
    pass


class UserSchema(pydantic.BaseModel):
    email: pydantic.EmailStr
    password: str
    is_superuser: bool = False
    roles: List[str] = pydantic.Field(default_factory=list)


class PermissionSchema(pydantic.BaseModel):
    resources: List[ResourceType]
    actions: List[Action]


class RoleSchema(pydantic.BaseModel):
    name: str
    description: str = ""
    permissions: List[PermissionSchema]


class DocumentSchema(pydantic.BaseModel):
    users: List[UserSchema]
    roles: List[RoleSchema]


async def create_roles(db: AsyncSession, roles: List[RoleSchema]):
    values = [role.dict(include={"name", "description"}) for role in roles]
    result = await db.execute(sa.insert(models.roles), values)
    logging.info("Roles created: {0!r}".format([r.name for r in roles]))

    for pk_row, role in zip(result.inserted_primary_key_rows, roles):
        role_id = pk_row[0]
        values = []
        for permission in role.permissions:
            for resource_type, action in itertools.product(
                permission.resources, permission.actions
            ):
                value = {
                    "role_id": role_id,
                    "resource_type": resource_type,
                    "action": action,
                }
                values.append(value)
        await db.execute(sa.insert(models.role_permissions), values)
        logging.info(f"Added {len(values)} permission for role {role.name!r}")


async def create_user(
    user_manager: UserManager, user: UserSchema
) -> models.User:
    user = await user_manager.create(
        schema.UserCreate(
            email=user.email,
            password=user.password,
            is_superuser=user.is_superuser,
        )
    )
    return user


async def assign_user_roles(
    db: AsyncSession, user: models.User, roles: List[str]
):
    for role_name in roles:
        role_id = await db.scalar(
            sa.select(models.roles.c.id).filter_by(name=role_name)
        )
        if role_id is None:
            raise ApplicationError("Role {role_name!r} not found.")
        await db.execute(
            sa.insert(models.user_roles).values(
                user_id=user.id, role_id=role_id
            )
        )
    logger.info(
        "User '{email}' has been assigned roles: {roles!r}".format(
            email=user.email, roles=roles
        )
    )


def load_document(path: str) -> DocumentSchema:
    with open(path) as fp:
        data = yaml.safe_load(fp)
    return DocumentSchema.parse_obj(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Initial data YAML document.")
    return parser.parse_args()


async def main(args: argparse.Namespace):
    config = load_settings()
    document = load_document(args.file)

    engine = engine_from_config(config)
    session_factory = create_session_factory(engine)
    async with dispose_context(engine), session_factory() as db:
        await create_roles(db, document.roles)
        user_db = get_user_db(config, db)
        user_manager = get_user_manager(config, user_db)
        for user in document.users:
            user_id = await create_user(user_manager, user)
            await assign_user_roles(db, user_id, user.roles)

        await db.commit()


def cli():
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s: %(message)s"
    )
    args = parse_args()
    try:
        return asyncio.run(main(args))
    except ApplicationError as e:
        logger.error(e)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(cli())
