import sqlalchemy as sa
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db import models
from ansible_events_ui.db.dependency import get_db_session

router = APIRouter()


@router.get("/api/rules/")
async def list_rules(db: AsyncSession = Depends(get_db_session)):
    query = (
        sa.select(
            models.rules.c.id,
            models.rules.c.name,
            models.rules.c.action,
            models.rulesets.c.id.label("ruleset_id"),
            models.rulesets.c.name.label("ruleset_name"),
        )
        .select_from(models.rules)
        .join(models.rulesets)
    )
    rows = (await db.execute(query)).all()

    response = []
    for row in rows:
        response.append(
            {
                "id": row["id"],
                "name": row["name"],
                "action": row["action"],
                "ruleset": {
                    "id": row["ruleset_id"],
                    "name": row["ruleset_name"],
                },
            }
        )
    return response


@router.get("/api/rules/{rule_id}/")
async def show_rule(rule_id: int, db: AsyncSession = Depends(get_db_session)):
    query = (
        sa.select(
            models.rules.c.id,
            models.rules.c.name,
            models.rules.c.action,
            models.rulesets.c.id.label("ruleset_id"),
            models.rulesets.c.name.label("ruleset_name"),
        )
        .select_from(models.rules)
        .join(models.rulesets)
        .filter(models.rules.c.id == rule_id)
    )
    row = (await db.execute(query)).first()
    return {
        "id": row["id"],
        "name": row["name"],
        "action": row["action"],
        "ruleset": {
            "id": row["ruleset_id"],
            "name": row["ruleset_name"],
        },
    }
