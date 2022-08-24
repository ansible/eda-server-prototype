import pytest
import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db import models

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


@pytest.mark.asyncio
async def test_create_rulebook(client: AsyncClient, db: AsyncSession):
    response = await client.post(
        "/api/rulebooks/",
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


@pytest.mark.asyncio
async def test_create_inventory(client: AsyncClient):
    response = await client.post(
        "/api/inventory/",
        json={
            "name": "test-inventory-01",
            "inventory": "all: {}",  # noqa: P103
        },
    )
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "test-inventory-01"
    assert data["inventory"] == "all: {}"  # noqa: P103


@pytest.mark.asyncio
async def test_list_inventories(client: AsyncClient, db: AsyncSession):
    query = sa.insert(models.inventories).values(
        name="test-list-inventories-01", inventory="{}"  # noqa: P103
    )
    result = await db.execute(query)

    response = await client.get("/api/inventories/")

    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert data == [
        {
            "id": result.inserted_primary_key[0],
            "name": "test-list-inventories-01",
            "inventory": "{}",  # noqa: P103
            "project_id": None,
        }
    ]
