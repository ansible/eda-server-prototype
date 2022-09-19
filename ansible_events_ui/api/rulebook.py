from typing import List

import sqlalchemy as sa
import yaml
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui import schema
from ansible_events_ui.db import models
from ansible_events_ui.db.dependency import get_db_session
from ansible_events_ui.project import insert_rulebook_related_data

router = APIRouter()


@router.get(
    "/api/rules/",
    response_model=List[schema.Rule],
    operation_id="list_rules",
)
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


@router.get(
    "/api/rules/{rule_id}/",
    response_model=schema.Rule,
    operation_id="show_rule",
)
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


@router.post("/api/rulebooks/")
async def create_rulebook(
    rulebook: schema.Rulebook, db: AsyncSession = Depends(get_db_session)
):
    query = sa.insert(models.rulebooks).values(
        name=rulebook.name, rulesets=rulebook.rulesets
    )
    result = await db.execute(query)
    (id_,) = result.inserted_primary_key

    rulebook_data = yaml.safe_load(rulebook.rulesets)
    await insert_rulebook_related_data(id_, rulebook_data, db)
    await db.commit()

    return {**rulebook.dict(), "id": id_}


@router.get("/api/rulebooks/")
async def list_rulebooks(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(models.rulebooks)
    result = await db.execute(query)
    return result.all()


@router.get("/api/rulebooks/{rulebook_id}")
async def read_rulebook(
    rulebook_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(models.rulebooks).where(
        models.rulebooks.c.id == rulebook_id
    )
    result = await db.execute(query)
    return result.first()


@router.get("/api/rulebook_json/{rulebook_id}")
async def read_rulebook_json(
    rulebook_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(models.rulebooks).where(
        models.rulebooks.c.id == rulebook_id
    )
    result = await db.execute(query)

    response = dict(result.first())
    response["rulesets"] = yaml.safe_load(response["rulesets"])
    return response
