from unittest import mock

import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.types import Action, ResourceType

TEST_RULESET_SIMPLE = """
---
- name: Test simple
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
"""


async def test_read_rulebook_not_found(client: AsyncClient):
    response = await client.get("/api/rulebooks/42")

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_create_rulebook(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    response = await client.post(
        "/api/rulebooks",
        json={
            "name": "test-ruleset-1.yml",
            "rulesets": TEST_RULESET_SIMPLE,
        },
    )
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "test-ruleset-1.yml"

    rulesets = (await db.execute(sa.select(models.rulesets))).all()
    assert len(rulesets) == 1
    ruleset = rulesets[0]
    assert ruleset["rulebook_id"] == data["id"]
    assert ruleset["name"] == "Test simple"

    rules = (await db.execute(sa.select(models.rules))).all()
    assert len(rules) == 1
    rule = rules[0]
    assert rule["ruleset_id"] == ruleset["id"]
    assert rule["action"] == {"debug": None}

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.RULEBOOK, Action.CREATE
    )
