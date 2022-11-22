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
from unittest import mock

import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.db.sql import base as bsql
from eda_server.types import Action, ResourceType

TEST_PROJECT = {
    "url": "https://git.example.com/sample/test-project",
    "name": "Test Name",
    "description": "This is a test description",
}

TEST_EXTRA_VAR = """
---
collections:
  - community.general
  - benthomasson.eda  # 1.3.0
"""


async def _create_dependent_project(db: AsyncSession):
    (project_id,) = (
        await bsql.insert_object(
            db,
            models.projects,
            values=TEST_PROJECT,
        )
    ).inserted_primary_key

    return project_id


async def _create_extra_var(db: AsyncSession):
    project_id = await _create_dependent_project(db)

    (extra_var_id,) = (
        await bsql.insert_object(
            db,
            models.extra_vars,
            values={
                "name": "test_extra_var",
                "extra_var": TEST_EXTRA_VAR,
                "project_id": project_id,
            },
        )
    ).inserted_primary_key

    return {"project_id": project_id, "extra_var_id": extra_var_id}


async def test_create_extar_var(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    project_id = await _create_dependent_project(db)
    await db.commit()

    response = await client.post(
        "/api/extra_vars/",
        json={
            "name": "test_create_extar_var",
            "extra_var": TEST_EXTRA_VAR,
            "project_id": project_id,
        },
    )
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert data["name"] == "test_create_extar_var"
    assert data["extra_var"] == TEST_EXTRA_VAR

    extra_vars = (await db.execute(sa.select(models.extra_vars))).all()
    assert len(extra_vars) == 1
    extra_var = extra_vars[0]
    assert extra_var["extra_var"] == TEST_EXTRA_VAR

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.EXTRA_VAR, Action.CREATE
    )


async def test_create_extar_var_bad_entity(
    client: AsyncClient, check_permission_spy: mock.Mock
):
    response = await client.post(
        "/api/extra_vars/",
        json=TEST_EXTRA_VAR,
    )
    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.EXTRA_VAR, Action.CREATE
    )


async def test_list_extra_vars(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    fks = await _create_extra_var(db)
    await db.commit()

    response = await client.get(
        "/api/extra_vars/",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    extra_vars = response.json()
    assert type(extra_vars) is list
    assert len(extra_vars) > 0

    extra_var = extra_vars[0]
    assert extra_var["id"] == fks["extra_var_id"]
    assert extra_var["name"] == "test_extra_var"
    assert extra_var["extra_var"] == TEST_EXTRA_VAR

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.EXTRA_VAR, Action.READ
    )


async def test_list_extra_vars_empty_response(
    client: AsyncClient, check_permission_spy: mock.Mock
):
    response = await client.get(
        "/api/extra_vars/",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    extra_vars = response.json()
    assert extra_vars == []

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.EXTRA_VAR, Action.READ
    )


async def test_read_extra_vars(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    fks = await _create_extra_var(db)
    await db.commit()

    extra_var_id = fks["extra_var_id"]
    response = await client.get(
        f"/api/extra_var/{extra_var_id}",
    )

    assert response.status_code == status_codes.HTTP_200_OK
    extra_var = response.json()
    assert "id" in extra_var

    assert extra_var["name"] == "test_extra_var"
    assert extra_var["extra_var"] == TEST_EXTRA_VAR

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.EXTRA_VAR, Action.READ
    )


async def test_read_extra_var_not_found(client: AsyncClient):
    response = await client.get("/api/extra_var/42")

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND
