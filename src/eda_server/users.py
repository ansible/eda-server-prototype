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

import logging
import uuid
from typing import Any, Dict, Optional

import sqlalchemy as sa
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import BaseUserDatabase, SQLAlchemyUserDatabase
from fastapi_users.password import PasswordHelperProtocol
from sqlalchemy.ext.asyncio import AsyncSession

from .config import Settings, get_settings
from .db import models
from .db.dependency import get_db_session

logger = logging.getLogger("eda_server.auth")


class RoleNotExists(Exception):
    pass


class UserDatabase(SQLAlchemyUserDatabase[models.User, uuid.UUID]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, models.User, None)

    async def _add_default_roles(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            sa.insert(models.user_roles).from_select(
                ["user_id", "role_id"],
                sa.select(sa.literal(user_id), models.roles.c.id).where(
                    models.roles.c.is_default.is_(True)
                ),
            )
        )

    async def create(self, create_dict: Dict[str, Any]) -> models.User:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.flush()
        await self._add_default_roles(user.id)
        await self.session.commit()
        await self.session.refresh(user)
        return user


class UserManager(UUIDIDMixin, BaseUserManager[models.User, uuid.UUID]):
    def __init__(
        self,
        secret: str,
        user_db: BaseUserDatabase[models.User, uuid.UUID],
        password_helper: Optional[PasswordHelperProtocol] = None,
    ):
        super().__init__(user_db, password_helper)

        self.reset_password_token_secret = secret
        self.verification_token_secret = secret

    async def on_after_register(
        self, user: models.User, request: Optional[Request] = None
    ):
        logger.info("User %s has registered.", user.id)

    async def on_after_forgot_password(
        self, user: models.User, token: str, request: Optional[Request] = None
    ):
        logger.info(
            "User %s has forgot their password. Reset token: %s",
            user.id,
            token,
        )

    async def on_after_request_verify(
        self, user: models.User, token: str, request: Optional[Request] = None
    ):
        logger.info(
            "Verification requested for user %s. Verification token: %s",
            user.id,
            token,
        )


def get_user_db(session: AsyncSession = Depends(get_db_session)):
    return UserDatabase(session)


def get_user_manager(
    settings: Settings = Depends(get_settings),
    user_db: UserDatabase = Depends(get_user_db),
):
    return UserManager(settings.secret, user_db)


def get_jwt_strategy(
    settings: Settings = Depends(get_settings),
) -> JWTStrategy:
    return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)


cookie_backend = AuthenticationBackend(
    name="jwt",
    transport=CookieTransport(cookie_max_age=3600),
    get_strategy=get_jwt_strategy,
)
bearer_backend = AuthenticationBackend(
    name="bearer",
    transport=BearerTransport(tokenUrl="auth/bearer/login"),
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[models.User, uuid.UUID](
    get_user_manager=get_user_manager,
    auth_backends=[cookie_backend, bearer_backend],
)

current_active_user = fastapi_users.current_user(active=True)
