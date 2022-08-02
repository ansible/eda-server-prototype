import logging
import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import BaseUserDatabase, SQLAlchemyUserDatabase
from fastapi_users.password import PasswordHelperProtocol
from sqlalchemy.ext.asyncio import AsyncSession

from .config import Settings, get_settings
from .db.models import User
from .db.session import get_db_session

logger = logging.getLogger("ansible_events_ui.auth")


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    def __init__(
        self,
        secret: str,
        user_db: BaseUserDatabase[User, uuid.UUID],
        password_helper: Optional[PasswordHelperProtocol] = None,
    ):
        super().__init__(user_db, password_helper)

        self.reset_password_token_secret = secret
        self.verification_token_secret = secret

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ):
        logger.info("User %s has registered.", user.id)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(
            "User %s has forgot their password. Reset token: %s",
            user.id,
            token,
        )

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(
            "Verification requested for user %s. Verification token: %s",
            user.id,
            token,
        )


async def get_user_db(session: AsyncSession = Depends(get_db_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
    settings: Settings = Depends(get_settings),
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
):
    yield UserManager(settings.secret, user_db)


def get_jwt_strategy(
    settings: Settings = Depends(get_settings),
) -> JWTStrategy:
    return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)


cookie_transport = CookieTransport(cookie_max_age=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
