import pytest
import sqlalchemy as sa
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as status_codes

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


async def _create_rules(db: AsyncSession):
    (rulebook_id,) = (
        await db.execute(
            sa.insert(models.rulebooks).values(
                name="test-ruleset-1.yml", rulesets=TEST_RULESET_SIMPLE
            )
        )
    ).inserted_primary_key

    (ruleset_id,) = (
        await db.execute(
            sa.insert(models.rulesets).values(
                name="Test simple",
                rulebook_id=rulebook_id,
            )
        )
    ).inserted_primary_key

    (rule_id,) = (
        await db.execute(
            sa.insert(models.rules).values(
                name=None, action={"debug": None}, ruleset_id=ruleset_id
            )
        )
    ).inserted_primary_key
    await db.commit()

    return rulebook_id, ruleset_id, rule_id


@pytest.mark.asyncio
async def test_list_rules(client: AsyncClient, db: AsyncSession):
    rulebook_id, ruleset_id, rule_id = await _create_rules(db)

    response = await client.get("/api/rules/")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == [
        {
            "id": rule_id,
            "name": None,
            "action": {"debug": None},
            "ruleset": {
                "id": ruleset_id,
                "name": "Test simple",
            },
        }
    ]


@pytest.mark.asyncio
async def test_read_rule(client: AsyncClient, db: AsyncSession):
    rulebook_id, ruleset_id, rule_id = await _create_rules(db)

    response = await client.get(f"/api/rules/{rule_id}/")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == {
        "id": rule_id,
        "name": None,
        "action": {"debug": None},
        "ruleset": {
            "id": ruleset_id,
            "name": "Test simple",
        },
    }
