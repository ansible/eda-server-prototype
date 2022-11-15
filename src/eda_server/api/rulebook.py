from decimal import Decimal
from typing import Dict, List

import yaml
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server import schema
from eda_server.db.dependency import get_db_session

# Rule, Ruleset, Rulebook query builder, enums, etc
from eda_server.db.sql import rulebook as rsql
from eda_server.project import insert_rulebook_related_data

router = APIRouter(tags=["rulebooks"])


# ------------------------------------
#   Stat result builders (rule, ruleset)
# ------------------------------------

# Builds a list of object details with a rule fire summary by status for a
# specified object.
async def build_object_list_totals(
    record_index: dict, object_id: int
) -> List[Dict]:
    if object_id not in record_index.get(rsql.OBJECT_TOTAL, {}):
        return []

    one_hundred_dec = Decimal(100)
    grand_total_int = record_index[rsql.WINDOW_TOTAL]["fired_count"]
    grand_total_dec = Decimal(grand_total_int)
    object_total_int = record_index[rsql.OBJECT_TOTAL][object_id][
        "fired_count"
    ]
    object_total_dec = Decimal(object_total_int)
    status_object_record_index = record_index[rsql.STATUS_OBJECT_TOTAL]
    object_totals = []

    for key in (
        key for key in status_object_record_index if key[1] == object_id
    ):
        data = status_object_record_index[key]
        status = key[0]
        status_object_count = data["fired_count"]
        object_totals.append(
            {
                "total_type": "status",
                "status": status,
                "status_total": status_object_count,
                "object_total": object_total_int,
                "pct_object_total": (
                    Decimal(status_object_count)
                    / object_total_dec
                    * one_hundred_dec
                ),
                "window_total": grand_total_int,
                "pct_window_total": (
                    Decimal(status_object_count)
                    / grand_total_dec
                    * one_hundred_dec
                ),
            }
        )

    return object_totals


# Builds a list of object details with a rule fire summary by
# date and status for a specified object.
async def build_detail_object_totals(
    record_index: dict, object_id: int
) -> List[Dict]:
    if object_id not in record_index.get(rsql.OBJECT_TOTAL, {}):
        return []

    one_hundred_dec = Decimal(100)
    grand_total_int = record_index[rsql.WINDOW_TOTAL]["fired_count"]
    grand_total_dec = Decimal(grand_total_int)
    date_status_object_record_index = record_index[
        rsql.DATE_STATUS_OBJECT_TOTAL
    ]
    object_totals = []

    last_date = date_status_total_int = date_status_total_dec = None
    for key in (
        key for key in date_status_object_record_index if key[2] == object_id
    ):
        rec = date_status_object_record_index[key]
        date_status_key = key[:2]
        fire_date = key[0]
        if fire_date != last_date:
            last_date = fire_date
            date_status_total_int = record_index[rsql.DATE_STATUS_TOTAL][
                date_status_key
            ]["fired_count"]
            date_status_total_dec = Decimal(date_status_total_int)
        object_totals.append(
            {
                "total_type": "date_status_object",
                "fired_date": rec["fired_date"],
                "object_status": rec["status"],
                "object_status_total": rec["fired_count"],
                "date_status_total": date_status_total_int,
                "pct_date_status_total": (
                    Decimal(rec["fired_count"])
                    / date_status_total_dec
                    * one_hundred_dec
                ),
                "window_total": grand_total_int,
                "pct_window_total": (
                    Decimal(rec["fired_count"])
                    / grand_total_dec
                    * one_hundred_dec
                ),
            }
        )

    return object_totals


# ------------------------------------
#   rules endpoints
# ------------------------------------


@router.get(
    "/api/rules",
    response_model=List[schema.RuleList],
    operation_id="list_rules",
)
async def list_rules(db: AsyncSession = Depends(get_db_session)):
    rules = await rsql.list_rules(db)
    if rules.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No rules found.",
        )

    rule_counts = await rsql.get_rule_counts(db)

    response = []
    for rule in rules:
        resp_obj = rule._asdict()
        resp_obj["fired_stats"] = await build_object_list_totals(
            rule_counts, rule.id
        )
        response.append(resp_obj)

    return response


@router.get(
    "/api/rules/{rule_id}",
    response_model=schema.RuleDetail,
    operation_id="read_rule",
)
async def read_rule(rule_id: int, db: AsyncSession = Depends(get_db_session)):
    rule = await rsql.get_rule(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found.",
        )

    rule_counts = await rsql.get_rule_counts(db, rule_id)
    response = rule._asdict()
    response["fired_stats"] = await build_detail_object_totals(
        rule_counts, rule.id
    )
    return response


# ------------------------------------
#   rulesets endpoints
# ------------------------------------


@router.get(
    "/api/rulesets",
    response_model=List[schema.RulesetList],
    operation_id="list_rulesets",
)
async def list_rulesets(db: AsyncSession = Depends(get_db_session)):
    rulesets = await rsql.list_rulesets(db)
    if rulesets.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No rulesets found.",
        )

    ruleset_counts = await rsql.get_ruleset_counts(db)

    response = []
    for ruleset in rulesets:
        resp_obj = ruleset._asdict()
        resp_obj["source_types"] = [
            src["type"] for src in (resp_obj["sources"] or [])
        ]
        resp_obj["fired_stats"] = await build_object_list_totals(
            ruleset_counts, ruleset.id
        )
        response.append(resp_obj)

    return response


@router.get(
    "/api/rulesets/{ruleset_id}",
    response_model=schema.RulesetDetail,
    operation_id="read_ruleset",
)
async def read_ruleset(
    ruleset_id: int, db: AsyncSession = Depends(get_db_session)
):
    ruleset = await rsql.get_ruleset(db, ruleset_id)
    if not ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruleset not found.",
        )

    ruleset_counts = await rsql.get_ruleset_counts(db, ruleset_id)
    response = ruleset._asdict()
    response["fired_stats"] = await build_detail_object_totals(
        ruleset_counts, ruleset.id
    )
    return response


@router.get(
    "/api/rulesets/{ruleset_id}/rules",
    response_model=List[schema.RuleList],
    operation_id="list_ruleset_rules",
)
async def list_ruleset_rules(
    ruleset_id: int, db: AsyncSession = Depends(get_db_session)
):
    ruleset_rules = await rsql.list_ruleset_rules(db, ruleset_id)
    if ruleset_rules.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ruleset not found"
        )
    return ruleset_rules.all()


# There used to be a separate query for rulesets/<id>/sources, but that data
# is being returned as part of the `get_ruleset` endpoint, so the separate
# endpoint is no longer needed.


# ------------------------------------
#   rulebooks endpoints
# ------------------------------------


@router.post(
    "/api/rulebooks",
    operation_id="create_rulebook",
)
async def create_rulebook(
    rulebook: schema.RulebookCreate, db: AsyncSession = Depends(get_db_session)
):
    try:
        new_rulebook = await rsql.create_rulebook(
            db,
            {
                "name": rulebook.name,
                "rulesets": rulebook.rulesets,
                "description": rulebook.description,
            },
        )
    except rsql.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unprocessable Entity.",
        )
    else:
        if new_rulebook is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unprocessable Entity.",
            )

    rulebook_data = yaml.safe_load(new_rulebook.rulesets)
    await insert_rulebook_related_data(db, new_rulebook.id, rulebook_data)
    await db.commit()

    return new_rulebook


@router.get(
    "/api/rulebooks",
    operation_id="list_rulebooks",
    response_model=List[schema.RulebookList],
)
async def list_rulebooks(db: AsyncSession = Depends(get_db_session)):
    rulebooks = await rsql.list_rulebooks(db)
    return rulebooks.all()


@router.get(
    "/api/rulebooks/{rulebook_id}",
    operation_id="read_rulebook",
    response_model=schema.RulebookRead,
)
async def read_rulebook(
    rulebook_id: int, db: AsyncSession = Depends(get_db_session)
):
    result = await rsql.get_rulebook(db, rulebook_id)
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
    result = await rsql.get_rulebook(db, rulebook_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rulebook Not Found.",
        )
    result = result._asdict()
    result["rulesets"] = yaml.safe_load(result["rulesets"])
    return result


@router.get(
    "/api/rulebooks/{rulebook_id}/rulesets",
    operation_id="list_rulebook_rulesets",
    response_model=List[schema.RulesetList],
)
async def list_rulebook_rulesets(
    rulebook_id: int, db: AsyncSession = Depends(get_db_session)
):
    rulebook_rulesets = await rsql.list_rulebook_rulesets(db, rulebook_id)
    if rulebook_rulesets.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rulebook Rulesets Not Found.",
        )
    rr_counts = await rsql.get_rulebook_ruleset_indexed_fired_counts(
        db, rulebook_id
    )

    response = []
    for ruleset in rulebook_rulesets:
        resp_obj = ruleset._asdict()
        resp_obj["source_types"] = [
            src["type"] for src in (resp_obj["sources"] or [])
        ]
        resp_obj["fired_stats"] = await build_object_list_totals(
            rr_counts, ruleset.id
        )
        response.append(resp_obj)

    return response

    return rulebook_rulesets.all()
