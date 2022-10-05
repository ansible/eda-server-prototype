from typing import List

import sqlalchemy as sa
import yaml
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server import schema
from eda_server.db import models
from eda_server.db.dependency import get_db_session
from eda_server.project import insert_rulebook_related_data

router = APIRouter(tags=["rulebooks"])


# ------------------------------------
#   rules endpoints
# ------------------------------------


@router.get(
    "/api/rules",
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
    "/api/rules/{rule_id}",
    response_model=schema.Rule,
    operation_id="read_rule",
)
async def read_rule(rule_id: int, db: AsyncSession = Depends(get_db_session)):
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


# ------------------------------------
#   rulesets endpoints
# ------------------------------------

# This query will leverage a left outer join lateral
# in order to get the rule counts.
ruleset = sa.orm.aliased(models.rulesets)
rules_lat = sa.orm.aliased(models.rules)
rulebook = sa.orm.aliased(models.rulebooks)
project = sa.orm.aliased(models.projects)

rule_count_lateral = (
    (
        sa.select(sa.func.count(rules_lat.c.id).label("rule_count"))
        .select_from(rules_lat)
        .filter(rules_lat.c.ruleset_id == ruleset.c.id)
    )
    .subquery()
    .lateral()
)
ruls_ct = sa.orm.aliased(rule_count_lateral)

BASE_RULESET_SELECT = (
    sa.select(
        ruleset.c.id,
        ruleset.c.name,
        ruleset.c.created_at,
        ruleset.c.modified_at,
        sa.func.coalesce(ruls_ct.c.rule_count, 0).label("rule_count"),
        sa.func.coalesce(
            sa.func.jsonb_build_object(
                "id", rulebook.c.id, "name", rulebook.c.name
            ),
            sa.func.jsonb_build_object("id", None, "name", None),
        ).label("rulebook"),
        sa.func.coalesce(
            sa.func.jsonb_build_object(
                "id", project.c.id, "name", project.c.name
            ),
            sa.func.jsonb_build_object("id", None, "name", None),
        ).label("project"),
    )
    .select_from(ruleset)
    .outerjoin(rulebook, rulebook.c.id == ruleset.c.rulebook_id)
    .outerjoin(project, project.c.id == rulebook.c.project_id)
    .outerjoin(ruls_ct, sa.true())
)


@router.get(
    "/api/rulesets",
    response_model=List[schema.Ruleset],
    operation_id="list_rulesets",
)
async def list_rulesets(db: AsyncSession = Depends(get_db_session)):
    cur = await db.execute(BASE_RULESET_SELECT)
    response = [rec._asdict() for rec in cur]
    return response


@router.get(
    "/api/rulesets/{ruleset_id}",
    response_model=schema.RulesetDetail,
    operation_id="read_ruleset",
)
async def get_ruleset(
    ruleset_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = BASE_RULESET_SELECT.filter(ruleset.c.id == ruleset_id)
    rec = (await db.execute(query)).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ruleset not found"
        )

    return rec._asdict()


# ------------------------------------
#   rulebooks endpoints
# ------------------------------------


@router.post("/api/rulebooks", operation_id="create_rulebook")
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


@router.get("/api/rulebooks", operation_id="list_rulebooks")
async def list_rulebooks(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(models.rulebooks)
    result = await db.execute(query)
    return result.all()


@router.get("/api/rulebooks/{rulebook_id}", operation_id="read_rulebook")
async def read_rulebook(
    rulebook_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(models.rulebooks).where(
        models.rulebooks.c.id == rulebook_id
    )
    result = (await db.execute(query)).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory Not Found.",
        )
    return result


@router.get(
    "/api/rulebook_json/{rulebook_id}", operation_id="read_rulebook_json"
)
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
