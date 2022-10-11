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
# TODO(sdonahue): Refactor to minimize aliasing tables
ruleset = sa.orm.aliased(models.rulesets)
rule = sa.orm.aliased(models.rules)
rulebook = sa.orm.aliased(models.rulebooks)
project = sa.orm.aliased(models.projects)
audit_rule = sa.orm.aliased(models.audit_rules)

rule_count_lateral = (
    (
        sa.select(sa.func.count(rule.c.id).label("rule_count"))
        .select_from(rule)
        .filter(rule.c.ruleset_id == ruleset.c.id)
    )
    .subquery()
    .lateral()
)
ruls_ct = sa.orm.aliased(rule_count_lateral)

ruleset_fire_count = (
    sa.select(
        ruleset.c.rulebook_id,
        audit_rule.c.ruleset_id,
        sa.func.count(audit_rule.c.id).label("fire_count"),
    )
    .select_from(ruleset)
    .group_by(ruleset.c.rulebook_id)
    .group_by(audit_rule.c.ruleset_id)
    .outerjoin(audit_rule, audit_rule.c.ruleset_id == ruleset.c.id)
).cte("ruleset_fire_count")

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

rulebook_ruleset_count = (
    sa.select(
        ruleset.c.rulebook_id,
        sa.func.count(ruleset.c.id).label("ruleset_count"),
    )
    .select_from(ruleset)
    .group_by(ruleset.c.rulebook_id)
    .outerjoin(rulebook, rulebook.c.id == ruleset.c.rulebook_id)
).cte("rulebook_ruleset_count")


rulebook_fire_count = (
    sa.select(
        ruleset_fire_count.c.rulebook_id,
        sa.func.sum(ruleset_fire_count.c.fire_count).label("fire_count"),
    )
    .select_from(ruleset_fire_count)
    .group_by(ruleset_fire_count.c.rulebook_id)
    .outerjoin(rulebook, rulebook.c.id == ruleset_fire_count.c.rulebook_id)
).cte("rulebook_fire_count")


@router.post("/api/rulebooks", operation_id="create_rulebook")
async def create_rulebook(
    rulebook: schema.RulebookCreate, db: AsyncSession = Depends(get_db_session)
):
    query = sa.insert(models.rulebooks).values(
        name=rulebook.name,
        rulesets=rulebook.rulesets,
        description=rulebook.description,
    )
    result = await db.execute(query)
    (id_,) = result.inserted_primary_key

    rulebook_data = yaml.safe_load(rulebook.rulesets)
    await insert_rulebook_related_data(id_, rulebook_data, db)
    await db.commit()

    return {**rulebook.dict(), "id": id_}


@router.get(
    "/api/rulebooks",
    operation_id="list_rulebooks",
    response_model=List[schema.RulebookList],
)
async def list_rulebooks(db: AsyncSession = Depends(get_db_session)):
    query = (
        sa.select(
            rulebook.c.id,
            rulebook.c.name,
            sa.func.coalesce(rulebook_ruleset_count.c.ruleset_count, 0).label(
                "ruleset_count"
            ),
            sa.func.coalesce(rulebook_fire_count.c.fire_count, 0).label(
                "fire_count"
            ),
        )
        .select_from(rulebook)
        .outerjoin(
            rulebook_ruleset_count,
            rulebook_ruleset_count.c.rulebook_id == rulebook.c.id,
        )
        .outerjoin(
            rulebook_fire_count,
            rulebook_fire_count.c.rulebook_id == rulebook.c.id,
        )
    )
    result = await db.execute(query)
    return result.all()


@router.get(
    "/api/rulebooks/{rulebook_id}",
    operation_id="read_rulebook",
    response_model=schema.RulebookRead,
)
async def read_rulebook(
    rulebook_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        sa.select(
            rulebook.c.id,
            rulebook.c.name,
            rulebook.c.description,
            rulebook.c.created_at,
            rulebook.c.modified_at,
            sa.func.coalesce(rulebook_ruleset_count.c.ruleset_count, 0).label(
                "ruleset_count"
            ),
            sa.func.coalesce(rulebook_fire_count.c.fire_count, 0).label(
                "fire_count"
            ),
        )
        .select_from(rulebook)
        .outerjoin(
            rulebook_ruleset_count,
            rulebook_ruleset_count.c.rulebook_id == rulebook.c.id,
        )
        .outerjoin(
            rulebook_fire_count,
            rulebook_fire_count.c.rulebook_id == rulebook.c.id,
        )
    ).filter(rulebook.c.id == rulebook_id)

    result = (await db.execute(query)).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rulebook Not Found.",
        )
    return result


@router.get(
    "/api/rulebook_json/{rulebook_id}", operation_id="read_rulebook_json"
)
async def read_rulebook_json(
    rulebook_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        sa.select(
            rulebook.c.id,
            rulebook.c.name,
            rulebook.c.description,
            rulebook.c.rulesets,
            sa.func.coalesce(rulebook_ruleset_count.c.ruleset_count, 0).label(
                "ruleset_count"
            ),
            sa.func.coalesce(rulebook_fire_count.c.fire_count, 0).label(
                "fire_count"
            ),
            rulebook.c.created_at,
            rulebook.c.modified_at,
        )
        .select_from(rulebook)
        .outerjoin(
            rulebook_ruleset_count,
            rulebook_ruleset_count.c.rulebook_id == rulebook.c.id,
        )
        .outerjoin(
            rulebook_fire_count,
            rulebook_fire_count.c.rulebook_id == rulebook.c.id,
        )
    ).filter(rulebook.c.id == rulebook_id)

    result = await db.execute(query)

    response = dict(result.first())
    response["rulesets"] = yaml.safe_load(response["rulesets"])
    return response


@router.get(
    "/api/rulebooks/{rulebook_id}/rulesets",
    operation_id="list_rulebook_rulesets",
    response_model=List[schema.RulebookRulesetList],
)
async def list_rulebook_rulesets(
    rulebook_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        sa.select(
            ruleset.c.id,
            ruleset.c.name,
            sa.func.coalesce(ruls_ct.c.rule_count, 0).label("rule_count"),
            sa.func.coalesce(ruleset_fire_count.c.fire_count, 0).label(
                "fire_count"
            ),
        )
        .select_from(ruleset)
        .outerjoin(
            ruls_ct,
            ruls_ct.c.rule_count == ruleset.c.id,
        )
        .outerjoin(
            ruleset_fire_count,
            ruleset_fire_count.c.fire_count == ruleset.c.id,
        )
        .outerjoin(rulebook, rulebook.c.id == ruleset.c.rulebook_id)
    ).filter(rulebook.c.id == rulebook_id)

    result = (await db.execute(query)).all()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rulebook Not Found.",
        )
    return result
