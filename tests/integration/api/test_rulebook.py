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
import yaml
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.db.sql import base as bsql
from eda_server.types import Action, ResourceType

TEST_RULESETS_SIMPLE = """
---
- name: Test simple 001
  hosts: all
  sources:
    - name: range
      range:
        limit: 5
  rules:
    - name:
      condition: event.i == 1
      action:
        debug:

- name: Test simple 002
  hosts: all
  sources:
    - name: range
      range:
        limit: 5
  rules:
    - name:
      condition: event.i == 2
      action:
        debug:
"""


async def _create_rulebook(db: AsyncSession):
    (rulebook_id,) = (
        await bsql.insert_object(
            db,
            models.rulebooks,
            values={
                "name": "test-ruleset-0110.yml",
                "rulesets": TEST_RULESETS_SIMPLE,
            },
        )
    ).inserted_primary_key

    return rulebook_id


async def test_read_rulebooks(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    rulebook_id = await _create_rulebook(db)
    await db.commit()

    response = await client.get(
        f"/api/rulebooks/{rulebook_id}",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    rulebook = response.json()

    assert rulebook["id"] == rulebook_id
    assert rulebook["name"] == "test-ruleset-0110.yml"

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.RULEBOOK, Action.READ
    )


async def test_read_rulebook_not_found(client: AsyncClient):
    response = await client.get("/api/rulebooks/42")

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_read_rulebook_json(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    rulebook_id = await _create_rulebook(db)
    await db.commit()

    response = await client.get(
        f"/api/rulebook_json/{rulebook_id}",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    rulebook_json = response.json()
    assert rulebook_json["id"] == rulebook_id
    assert rulebook_json["name"] == "test-ruleset-0110.yml"
    assert rulebook_json["rulesets"] == yaml.safe_load(TEST_RULESETS_SIMPLE)

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.RULEBOOK, Action.READ
    )


async def test_create_rulebook(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    response = await client.post(
        "/api/rulebooks",
        json={
            "name": "test-ruleset-1.yml",
            "rulesets": TEST_RULESETS_SIMPLE,
        },
    )
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "test-ruleset-1.yml"

    rulesets = (await db.execute(sa.select(models.rulesets))).all()
    assert len(rulesets) == 2
    ruleset = rulesets[0]
    assert ruleset["rulebook_id"] == data["id"]
    assert (
        ruleset["name"].startswith("Test simple ")
        and ruleset["name"][-3:].isdigit()
    )

    rules = (await db.execute(sa.select(models.rules))).all()
    assert len(rules) == 2
    rule = rules[0]
    assert rule["ruleset_id"] == ruleset["id"]
    assert rule["action"] == {"debug": None}

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.RULEBOOK, Action.CREATE
    )


async def test_list_rulebooks(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    rulebook_id = await _create_rulebook(db)
    await db.commit()

    response = await client.get("/api/rulebooks")
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == rulebook_id

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.RULEBOOK, Action.READ
    )


async def test_list_rulebooks_empty_response(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    response = await client.get(
        "/api/rulebooks",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    rulebooks = response.json()
    assert rulebooks == []

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.RULEBOOK, Action.READ
    )


async def test_list_rulebook_rulesets(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    response = await client.post(
        "/api/rulebooks",
        json={
            "name": "test-ruleset-0110.yml",
            "rulesets": TEST_RULESETS_SIMPLE,
        },
    )

    assert response.status_code == status_codes.HTTP_200_OK

    rulebook = response.json()
    response = await client.get(f"/api/rulebooks/{rulebook['id']}/rulesets")
    rulebook_rulesets = response.json()

    r_ct = (
        sa.select(sa.func.count().label("rule_count"))
        .select_from(models.rules)
        .filter(models.rules.c.ruleset_id == models.rulesets.c.id)
        .subquery()
        .lateral()
    )
    rulesets = (
        await db.execute(
            sa.select(
                models.rulesets.c.id, models.rulesets.c.name, r_ct.c.rule_count
            )
            .select_from(models.rulesets)
            .outerjoin(r_ct, sa.true())
            .filter(models.rulesets.c.rulebook_id == rulebook["id"])
        )
    ).all()

    assert len(rulebook_rulesets) == len(rulesets) == 2

    for ix in range(len(rulebook_rulesets)):
        assert rulebook_rulesets[ix]["id"] == rulesets[ix].id
        assert rulebook_rulesets[ix]["name"] == rulesets[ix].name
        assert rulebook_rulesets[ix]["rule_count"] == rulesets[ix].rule_count

    check_permission_spy.assert_called_with(
        mock.ANY, mock.ANY, ResourceType.RULEBOOK, Action.READ
    )
