#!/usr/bin/env python
# TODO(cutwater): Move to eda_server.cli package
# TODO(cutwater): Add integration tests for this script
import argparse
import asyncio
import getpass
import logging
import os
import sys

import pydantic
from fastapi_users.exceptions import UserAlreadyExists

from eda_server.config import load_settings
from eda_server.db.session import create_session_factory, engine_from_config
from eda_server.schema import UserCreate
from eda_server.users import RoleNotExists, get_user_db, get_user_manager

logger = logging.getLogger()


EXIT_SUCCESS = 0
EXIT_ERROR = 1


class ApplicationError(Exception):
    pass


async def create_user(
    email: str,
    password: str,
    is_superuser: bool = False,
):
    config = load_settings()
    engine = engine_from_config(config)
    session_factory = create_session_factory(engine)

    async with session_factory() as db:
        user_db = get_user_db(config, db)
        user_manager = get_user_manager(config, user_db)

        try:
            data = UserCreate(
                email=email, password=password, is_superuser=is_superuser
            )
        except pydantic.ValidationError as e:
            message = "Invalid data"
            for err in e.errors():
                if err["loc"] == ("email",):
                    message = "Invalid email address"
                    break
            raise ApplicationError(message)

        try:
            await user_manager.create(data)
        except UserAlreadyExists:
            raise ApplicationError(f"User '{email}' already exists.")
        except RoleNotExists as e:
            raise ApplicationError(str(e))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-S",
        "--superuser",
        action="store_true",
        help="create superuser",
        dest="is_superuser",
        default=False,
    )
    parser.add_argument(
        "-E",
        help="read password from environment variable",
        action="store_true",
        dest="password_from_env",
    )
    parser.add_argument("--password", help="set user password")
    parser.add_argument(
        "--password-envvar",
        default="PASSWORD",
        help="set environment variable to read password from",
        metavar="name",
    )
    parser.add_argument("email", help="user email address")
    return parser.parse_args()


def read_password(args) -> str:
    if args.password is not None:
        password = args.password
        if not password:
            raise ApplicationError("Password cannot be empty.")
        logger.warning(
            "Specifying passwords in command line arguments is insecure."
        )
        return password

    if args.password_from_env:
        envvar = args.password_envvar
        password = os.getenv(args.password_envvar)
        if password is None:
            raise ApplicationError(
                f"Environment variable '{envvar}' is not set."
            )
        return password

    password = getpass.getpass("Enter password: ")
    password_confirm = getpass.getpass("Confirm password: ")
    if not password:
        raise ApplicationError("Password cannot be empty.")
    if password != password_confirm:
        raise ApplicationError("Passwords don't match.")
    return password


async def main(args: argparse.Namespace):
    await create_user(
        email=args.email,
        password=read_password(args),
        is_superuser=args.is_superuser,
    )


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
