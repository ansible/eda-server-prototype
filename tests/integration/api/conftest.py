from unittest import mock

import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.auth import check_permission
from eda_server.db import models
from eda_server.users import UserDatabase, current_active_user
from tests.integration.utils.app import override_dependencies


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession):
    user = await UserDatabase(db).create(
        {
            "email": "admin@example.com",
            "hashed_password": "",
            "is_superuser": True,
        }
    )
    # NOTE(cutwater): Commit transaction implicitly opened by
    #   UserDatabase as a side effect. Need better API for creating users.
    await db.commit()
    return user


@pytest.fixture
def app(app: FastAPI, admin_user: models.User):
    dependencies = {
        current_active_user: lambda: admin_user,
    }
    with override_dependencies(app, dependencies):
        yield app


@pytest.fixture
def check_permission_spy():
    m = mock.AsyncMock(wraps=check_permission)
    with mock.patch("eda_server.auth.check_permission", m):
        yield m
