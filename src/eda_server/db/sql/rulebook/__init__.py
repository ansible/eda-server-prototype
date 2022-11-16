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

"""Query builders and executors for rule, ruleset, rulebook endpoints."""

import datetime
import enum
from typing import Dict, List, Optional, Tuple, Union

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.db.sql import base as bsql

WINDOW_TOTAL = "window_total"
DATE_TOTAL = "date_total"
STATUS_TOTAL = "status_total"
OBJECT_TOTAL = "object_total"
DATE_STATUS_TOTAL = "date_status_total"
DATE_OBJECT_TOTAL = "date_object_total"
STATUS_OBJECT_TOTAL = "status_object_total"
DATE_STATUS_OBJECT_TOTAL = "date_status_object_total"


class AuditGrouping(enum.Enum):
    RULE = 0
    RULESET = 1


class RulebookQueryEception(Exception):
    pass


# ------------------------------------
#   aliases
# ------------------------------------

# shorter variable names
ruleset = models.rulesets
rule = models.rules
rulebook = models.rulebooks
project = models.projects
audit_rule = models.audit_rules

# table aliases
a_ruleset = sa.orm.aliased(ruleset, name="a_rs")
a_rulebook = sa.orm.aliased(rulebook, name="a_rb")
a_rule = sa.orm.aliased(rule, name="a_ru")
a_project = sa.orm.aliased(project, name="a_pr")
a_audit_rule = sa.orm.aliased(audit_rule, name="a_ar")


# ------------------------------------
#   Mapping from grouping enum to table column
# ------------------------------------

AUDIT_GROUPING = {
    AuditGrouping.RULE: a_audit_rule.c.rule_id,
    AuditGrouping.RULESET: a_audit_rule.c.ruleset_id,
}


# ------------------------------------
#   Query builders for ruleset
# ------------------------------------


def build_ruleset_base_query(object_id: Optional[int] = None) -> sa.sql.Select:
    rule_lat = sa.orm.aliased(models.rules, name="rule_lat")
    subq_select_exprs = [sa.func.count().label("rule_count")]
    subq_filters = rule_lat.c.ruleset_id == a_ruleset.c.id
    lat_count_subq = (
        bsql.build_object_query(
            select_cols=subq_select_exprs,
            select_from=rule_lat,
            filters=subq_filters,
        )
        .subquery("lat_count")
        .lateral()
    )
    select_exprs = [
        a_ruleset,
        lat_count_subq.c.rule_count,
        sa.func.jsonb_build_object(
            "id", a_rulebook.c.id, "name", a_rulebook.c.name
        ).label("rulebook"),
        sa.func.jsonb_build_object(
            "id", a_project.c.id, "name", a_project.c.name
        ).label("project"),
    ]
    select_from = (
        a_ruleset.outerjoin(
            a_rulebook, a_rulebook.c.id == a_ruleset.c.rulebook_id
        )
        .outerjoin(a_project, a_project.c.id == a_rulebook.c.project_id)
        .outerjoin(lat_count_subq, sa.true())
    )

    if object_id is not None:
        filters = a_ruleset.c.id == object_id
    else:
        filters = None

    base_query = bsql.build_object_query(
        select_from, select_cols=select_exprs, filters=filters
    )

    return base_query


# This will build the select columns for the grouping counts and
# will also build the grouping sets for those columns
# The return object is a dict
def get_count_cols_and_grouping(grouping: AuditGrouping) -> Dict:
    grouping_column = AUDIT_GROUPING[grouping]

    raw_select_cols = [
        sa.cast(a_audit_rule.c.fired_date, sa.Date).label("fired_date"),
        sa.func.count().label("fired_count"),
        a_audit_rule.c.status,
        grouping_column,
    ]

    grouping_set_tuples = (
        # date, status, object
        sa.tuple_(
            sa.cast(a_audit_rule.c.fired_date, sa.Date),
            a_audit_rule.c.status,
            grouping_column,
        ),
        # status, object
        sa.tuple_(
            a_audit_rule.c.status,
            grouping_column,
        ),
        # date, object
        sa.tuple_(
            sa.cast(a_audit_rule.c.fired_date, sa.Date),
            grouping_column,
        ),
        # date, status
        sa.tuple_(
            sa.cast(a_audit_rule.c.fired_date, sa.Date),
            a_audit_rule.c.status,
        ),
        # date
        sa.tuple_(
            sa.cast(a_audit_rule.c.fired_date, sa.Date),
        ),
        # status
        sa.tuple_(
            a_audit_rule.c.status,
        ),
        # object
        sa.tuple_(
            grouping_column,
        ),
        # window
        sa.tuple_(),
    )

    query_parts = {
        "raw_select_cols": raw_select_cols,
        "grouping_set_tuples": grouping_set_tuples,
    }
    return query_parts


# Thic function will build the inner query that will aggregate
# the audit_rule data to return the grouped set counts for the
# particular level of granularity.
def build_rule_count_subquery(
    grouping: AuditGrouping,
    query_parts: Dict,
    object_id: Optional[int] = None,
    *,
    window_start: Optional[datetime.datetime] = None,
    window_end: Optional[datetime.datetime] = None,
    select_from: Optional[sa.sql.TableClause] = a_audit_rule,
    filters: Optional[sa.sql.ColumnElement] = None,
) -> sa.sql.Select:
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    if window_start is None:
        window_start = datetime.datetime(
            *((now - datetime.timedelta(days=30)).timetuple()[:3]),
            tzinfo=datetime.timezone.utc,
        )
    else:
        window_start = datetime.datetime(
            *window_start.timetuple()[:3], tzinfo=datetime.timezone.utc
        )
    if window_end is None:
        window_end = now
    else:
        if window_end.tzinfo is None:
            window_end = window_end.replace(tzinfo=datetime.timezone.utc)

    rules_fired_count_sub = sa.select(
        *query_parts["raw_select_cols"]
    ).select_from(select_from)

    rules_fired_count_sub = rules_fired_count_sub.filter(
        a_audit_rule.c.fired_date.between(window_start, window_end)
    )

    if object_id is not None:
        rules_fired_count_sub = rules_fired_count_sub.filter(
            AUDIT_GROUPING[grouping] == object_id
        )

    if filters is not None:
        rules_fired_count_sub = rules_fired_count_sub.filter(filters)

    rules_fired_count_sub = rules_fired_count_sub.group_by(
        sa.func.grouping_sets(*query_parts["grouping_set_tuples"])
    ).subquery("rules_fired_count_sub")

    return rules_fired_count_sub


def get_row_type_case_conditions(
    grouping: AuditGrouping,
    rules_fired_count_sub: sa.sql.Executable,
) -> List[Tuple[sa.sql.elements.WrapsColumnExpression, str]]:
    grouping_column = AUDIT_GROUPING[grouping]
    cases = [
        (
            sa.and_(
                rules_fired_count_sub.c.fired_date.is_(None),
                rules_fired_count_sub.c.status.is_(None),
                rules_fired_count_sub.c[grouping_column.name].is_(None),
            ),
            "1_" + WINDOW_TOTAL,
        ),
        (
            sa.and_(
                rules_fired_count_sub.c.fired_date.is_not(None),
                rules_fired_count_sub.c.status.is_(None),
                rules_fired_count_sub.c[grouping_column.name].is_(None),
            ),
            "2_" + DATE_TOTAL,
        ),
        (
            sa.and_(
                rules_fired_count_sub.c.fired_date.is_(None),
                rules_fired_count_sub.c.status.is_not(None),
                rules_fired_count_sub.c[grouping_column.name].is_(None),
            ),
            "3_" + STATUS_TOTAL,
        ),
        (
            sa.and_(
                rules_fired_count_sub.c.fired_date.is_(None),
                rules_fired_count_sub.c.status.is_(None),
                rules_fired_count_sub.c[grouping_column.name].is_not(None),
            ),
            "4_" + OBJECT_TOTAL,
        ),
        (
            sa.and_(
                rules_fired_count_sub.c.fired_date.is_not(None),
                rules_fired_count_sub.c.status.is_(None),
                rules_fired_count_sub.c[grouping_column.name].is_not(None),
            ),
            "5_" + DATE_OBJECT_TOTAL,
        ),
        (
            sa.and_(
                rules_fired_count_sub.c.fired_date.is_not(None),
                rules_fired_count_sub.c.status.is_not(None),
                rules_fired_count_sub.c[grouping_column.name].is_(None),
            ),
            "6_" + DATE_STATUS_TOTAL,
        ),
        (
            sa.and_(
                rules_fired_count_sub.c.fired_date.is_(None),
                rules_fired_count_sub.c.status.is_not(None),
                rules_fired_count_sub.c[grouping_column.name].is_not(None),
            ),
            "7_" + STATUS_OBJECT_TOTAL,
        ),
        (
            sa.and_(
                rules_fired_count_sub.c.fired_date.is_not(None),
                rules_fired_count_sub.c.status.is_not(None),
                rules_fired_count_sub.c[grouping_column.name].is_not(None),
            ),
            "8_" + DATE_STATUS_OBJECT_TOTAL,
        ),
    ]

    return cases


def build_labeled_count_query(
    grouping: AuditGrouping,
    rules_fired_count_sub: sa.sql.Executable,
) -> sa.sql.Executable:
    case_label_expr = get_row_type_case_conditions(
        grouping, rules_fired_count_sub
    )
    labeled_counts = (
        sa.select(
            sa.case(*case_label_expr).label("row_type"),
            rules_fired_count_sub,
        )
        .select_from(rules_fired_count_sub)
        .order_by("row_type")
    )

    return labeled_counts


# Assemble the subquery and outer object reference query
# And return the final query form.
def build_object_fire_counts_query(
    grouping: AuditGrouping,
    object_id: Optional[int] = None,
    *,
    window_start: Optional[datetime.datetime] = None,
    window_end: Optional[datetime.datetime] = None,
) -> sa.sql.Select:
    query_parts = get_count_cols_and_grouping(grouping)
    rule_count_subquery = build_rule_count_subquery(
        grouping,
        query_parts,
        object_id,
        window_start=window_start,
        window_end=window_end,
    )

    rule_fired_counts_query = build_labeled_count_query(
        grouping, rule_count_subquery
    )

    return rule_fired_counts_query


def build_rulebook_rulesets_fire_counts_query(
    rulebook_id: int,
    *,
    window_start: Optional[datetime.datetime] = None,
    window_end: Optional[datetime.datetime] = None,
) -> sa.sql.Select:
    query_parts = get_count_cols_and_grouping(AuditGrouping.RULESET)
    rb_rs_count_subquery = build_rule_count_subquery(
        AuditGrouping.RULESET,
        query_parts,
        object_id=None,
        window_start=window_start,
        window_end=window_end,
        select_from=(
            a_audit_rule.outerjoin(
                a_ruleset, a_ruleset.c.id == a_audit_rule.c.ruleset_id
            )
        ),
        filters=(a_ruleset.c.rulebook_id == rulebook_id),
    )

    rb_rs_fired_counts_query = build_labeled_count_query(
        AuditGrouping.RULESET, rb_rs_count_subquery
    )

    return rb_rs_fired_counts_query


# ------------------------------------
#   Primary Public Functions for getting fired counts for ruleset, rule
# ------------------------------------


async def get_fired_counts(
    db: AsyncSession,
    grouping: AuditGrouping,
    object_id: Optional[int] = None,
    *,
    window_start: Optional[datetime.datetime] = None,
    window_end: Optional[datetime.datetime] = None,
) -> sa.engine.CursorResult:
    rule_fired_stats_query = build_object_fire_counts_query(
        grouping,
        object_id=object_id,
        window_start=window_start,
        window_end=window_end,
    )
    cur = await bsql.execute_get_results(db, rule_fired_stats_query)
    return cur


async def index_grouped_objects(
    cur: Union[sa.engine.CursorResult, List[sa.engine.Row]],
    grouping: AuditGrouping,
) -> Dict:
    grouped_column = AUDIT_GROUPING[grouping]
    counts = {}
    for rec in cur:
        drec = rec._asdict()
        drec["grouped_column_name"] = grouped_column.name
        row_type_key = drec["row_type"][2:]

        if row_type_key == WINDOW_TOTAL:
            counts[row_type_key] = drec
            continue
        elif row_type_key == STATUS_TOTAL:
            drec["key"] = drec["status"]
        elif row_type_key == DATE_TOTAL:
            drec["key"] = drec["fired_date"]
        elif row_type_key == OBJECT_TOTAL:
            drec["key"] = drec[grouped_column.name]
        elif row_type_key == STATUS_OBJECT_TOTAL:
            drec["key"] = (drec["status"], drec[grouped_column.name])
        elif row_type_key == DATE_OBJECT_TOTAL:
            drec["key"] = (drec["fired_date"], drec[grouped_column.name])
        elif row_type_key == DATE_STATUS_TOTAL:
            drec["key"] = (drec["fired_date"], drec["status"])
        elif row_type_key == DATE_STATUS_OBJECT_TOTAL:
            drec["key"] = (
                drec["fired_date"],
                drec["status"],
                drec[grouped_column.name],
            )

        counts.setdefault(row_type_key, {})[drec["key"]] = drec

    return counts


async def get_indexed_fired_counts(
    db: AsyncSession,
    grouping: AuditGrouping,
    object_id: Optional[int] = None,
    *,
    window_start: Optional[datetime.datetime] = None,
    window_end: Optional[datetime.datetime] = None,
) -> Dict:
    cur = await get_fired_counts(
        db,
        grouping,
        object_id,
        window_start=window_start,
        window_end=window_end,
    )
    indexed = await index_grouped_objects(cur, grouping)
    return indexed


async def get_rulebook_ruleset_fired_counts(
    db: AsyncSession,
    rulebook_id: int,
    *,
    window_start: Optional[datetime.datetime] = None,
    window_end: Optional[datetime.datetime] = None,
) -> sa.engine.CursorResult:
    rb_rs_fired_stats_query = build_rulebook_rulesets_fire_counts_query(
        rulebook_id,
        window_start=window_start,
        window_end=window_end,
    )
    cur = await bsql.execute_get_results(db, rb_rs_fired_stats_query)
    return cur


async def get_rulebook_ruleset_indexed_fired_counts(
    db: AsyncSession,
    rulebook_id: int,
    *,
    window_start: Optional[datetime.datetime] = None,
    window_end: Optional[datetime.datetime] = None,
) -> Dict:
    cur = await get_rulebook_ruleset_fired_counts(
        db,
        rulebook_id,
        window_start=window_start,
        window_end=window_end,
    )
    indexed = await index_grouped_objects(cur, AuditGrouping.RULESET)
    return indexed


async def list_rulesets(db: AsyncSession) -> sa.engine.CursorResult:
    query = build_ruleset_base_query()
    return await bsql.execute_get_results(db, query)


async def get_ruleset(db: AsyncSession, ruleset_id: int) -> sa.engine.Row:
    query = build_ruleset_base_query(ruleset_id)
    return await bsql.execute_get_result(db, query)


async def get_ruleset_counts(
    db: AsyncSession, ruleset_id: Optional[int] = None
) -> Dict:
    ruleset_counts = await get_indexed_fired_counts(
        db, AuditGrouping.RULESET, ruleset_id
    )
    return ruleset_counts


async def list_ruleset_rules(
    db: AsyncSession, ruleset_id: int
) -> sa.engine.CursorResult:
    query = build_rule_base_query()
    query = query.filter(a_rule.c.ruleset_id == ruleset_id)
    return await bsql.execute_get_results(db, query)


# ------------------------------------
#   Query builders for rules
# ------------------------------------


def build_rule_base_query(object_id: Optional[int] = None) -> sa.sql.Select:
    select_exprs = [
        a_rule,
        sa.func.jsonb_build_object(
            "id", a_ruleset.c.id, "name", a_ruleset.c.name
        ).label("ruleset"),
        sa.func.jsonb_build_object(
            "id", a_rulebook.c.id, "name", a_rulebook.c.name
        ).label("rulebook"),
        sa.func.jsonb_build_object(
            "id", a_project.c.id, "name", a_project.c.name
        ).label("project"),
    ]
    select_from = (
        a_rule.outerjoin(a_ruleset, a_ruleset.c.id == a_rule.c.ruleset_id)
        .outerjoin(a_rulebook, a_rulebook.c.id == a_ruleset.c.rulebook_id)
        .outerjoin(a_project, a_project.c.id == a_rulebook.c.project_id)
    )

    if object_id is not None:
        filters = a_rule.c.id == object_id
    else:
        filters = None

    base_query = bsql.build_object_query(
        select_from, select_cols=select_exprs, filters=filters
    )

    return base_query


async def list_rules(db: AsyncSession) -> sa.engine.CursorResult:
    query = build_rule_base_query()
    return await bsql.execute_get_results(db, query)


async def get_rule(db: AsyncSession, rule_id: int) -> sa.engine.Row:
    query = build_rule_base_query(rule_id)
    return await bsql.execute_get_result(db, query)


async def get_rule_counts(
    db: AsyncSession, rule_id: Optional[int] = None
) -> Dict:
    rule_counts = await get_indexed_fired_counts(
        db, AuditGrouping.RULE, rule_id
    )
    return rule_counts


# ------------------------------------
#   Query builders, actions for rulebooks
# ------------------------------------


async def create_rulebook(
    db: AsyncSession,
    rulebook_rec: Dict,
) -> sa.engine.Row:
    try:
        new_rulebook = (
            await bsql.insert_object(
                db, rulebook, values=rulebook_rec, returning=[rulebook]
            )
        ).one()
    except Exception as e:
        raise_exception(e)

    return new_rulebook


def build_rulebook_base_query(
    object_id: Optional[int] = None,
) -> sa.sql.Select:
    ruleset_lat = sa.orm.aliased(models.rulesets, name="ruleset_lat")
    subq_select_exprs = [sa.func.count().label("ruleset_count")]
    subq_filters = ruleset_lat.c.rulebook_id == a_rulebook.c.id
    lat_count_subq = (
        bsql.build_object_query(
            select_cols=subq_select_exprs,
            select_from=ruleset_lat,
            filters=subq_filters,
        )
        .subquery("lat_count")
        .lateral()
    )

    select_exprs = [
        a_rulebook,
        lat_count_subq.c.ruleset_count,
        sa.func.jsonb_build_object(
            "id", a_project.c.id, "name", a_project.c.name
        ).label("project"),
    ]
    select_from = a_rulebook.outerjoin(
        a_project, a_project.c.id == a_rulebook.c.project_id
    ).outerjoin(lat_count_subq, sa.true())

    if object_id is not None:
        filters = a_rulebook.c.id == object_id
    else:
        filters = None

    base_query = bsql.build_object_query(
        select_from, select_cols=select_exprs, filters=filters
    )

    return base_query


async def list_rulebooks(db: AsyncSession) -> sa.engine.CursorResult:
    query = build_rulebook_base_query()
    return await bsql.execute_get_results(db, query)


async def get_rulebook(db: AsyncSession, rulebook_id: int) -> sa.engine.Row:
    query = build_rulebook_base_query(rulebook_id)
    return await bsql.execute_get_result(db, query)


async def list_rulebook_rulesets(
    db: AsyncSession, rulebook_id: int
) -> sa.engine.CursorResult:
    query = build_ruleset_base_query()
    query = query.filter(a_ruleset.c.rulebook_id == rulebook_id)
    return await bsql.execute_get_results(db, query)


# Adds a common base class to mark any exception coming from this module code
def raise_exception(exc: Exception):
    err = type(
        exc.__class__.__name__, (exc.__class__, RulebookQueryEception), {}
    )
    raise err(str(exc))
