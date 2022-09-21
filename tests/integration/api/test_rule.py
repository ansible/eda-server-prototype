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
    project = (
        await db.execute(
            sa.insert(models.projects)
            .values(name="project--test-ruleset-1.yml")
            .returning(models.projects.c.id, models.projects.c.name)
        )
    ).first()

    rulebook = (
        await db.execute(
            sa.insert(models.rulebooks)
            .values(
                name="test--ruleset-1.yml",
                rulesets=TEST_RULESET_SIMPLE,
                project_id=project.id,
            )
            .returning(models.rulebooks.c.id, models.rulebooks.c.name)
        )
    ).first()

    ruleset = (
        await db.execute(
            sa.insert(models.rulesets)
            .values(
                name="Test--simple",
                rulebook_id=rulebook.id,
            )
            .returning(
                models.rulesets.c.id,
                models.rulesets.c.name,
                models.rulesets.c.rulebook_id,
                models.rulesets.c.created_at,
                models.rulesets.c.modified_at,
            )
        )
    ).first()

    rules = (
        await db.execute(
            sa.insert(models.rules)
            .values(
                [
                    {
                        "name": "rule--1",
                        "action": {"debug": None},
                        "ruleset_id": ruleset.id,
                    },
                    {
                        "name": "rule--2",
                        "action": {"debug": "eek"},
                        "ruleset_id": ruleset.id,
                    },
                ]
            )
            .returning(
                models.rules.c.id,
                models.rules.c.name,
                models.rules.c.action,
                models.rules.c.ruleset_id,
            )
        )
    ).all()
    await db.commit()

    return project, rulebook, ruleset, rules


@pytest.mark.asyncio
async def test_list_rules(client: AsyncClient, db: AsyncSession):
    _, _, ruleset, rules = await _create_rules(db)

    response = await client.get("/api/rules/")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == [
        {
            "id": rules[0].id,
            "name": rules[0].name,
            "action": rules[0].action,
            "ruleset": {
                "id": ruleset.id,
                "name": ruleset.name,
            },
        },
        {
            "id": rules[1].id,
            "name": rules[1].name,
            "action": rules[1].action,
            "ruleset": {
                "id": ruleset.id,
                "name": ruleset.name,
            },
        },
    ]


@pytest.mark.asyncio
async def test_read_rule(client: AsyncClient, db: AsyncSession):
    _, _, ruleset, rules = await _create_rules(db)

    response = await client.get(f"/api/rules/{rules[0].id}/")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == {
        "id": rules[0].id,
        "name": rules[0].name,
        "action": rules[0].action,
        "ruleset": {
            "id": ruleset.id,
            "name": ruleset.name,
        },
    }


@pytest.mark.asyncio
async def test_list_rulesets(client: AsyncClient, db: AsyncSession):
    _, rulebook, ruleset, rules = await _create_rules(db)

    response = await client.get("/api/rulesets/")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == [
        {
            "id": ruleset.id,
            "name": ruleset.name,
            "rule_count": len(rules),
        }
    ]


@pytest.mark.asyncio
async def test_read_ruleset(client: AsyncClient, db: AsyncSession):
    project, rulebook, ruleset, rules = await _create_rules(db)
    response = await client.get(f"/api/rulesets/{ruleset.id}/")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == {
        "id": ruleset.id,
        "name": ruleset.name,
        "rule_count": len(rules),
        "created_at": ruleset.created_at.isoformat(),
        "modified_at": ruleset.modified_at.isoformat(),
        "rulebook": {
            "id": rulebook.id,
            "name": rulebook.name,
        },
        "project": {
            "id": project.id,
            "name": project.name,
        },
    }


@pytest.mark.asyncio
async def test_read_ruleset_not_found(client: AsyncClient, db: AsyncSession):
    response = await client.get("/api/rulesets/-1/")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND
