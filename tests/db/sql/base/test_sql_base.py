import os
import pytest
import sqlalchemy as sa
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as status_codes

from eda_server.db import models
from eda_server.db.sql import base as bsql


async def test_build_select_query():
    query = bsql.build_object_query(
        models.audit_rules,
        select_cols=[
            models.audit_rules.c.ruleset_id,
            sa.func.count().label("rule_count"),
        ],
        filters=models.audit_rules.c.rule_id.is_not(None),
        group_by=[models.audit_rules.c.ruleset_id],
        having=sa.func.count() > 1,
        order_by=[sa.desc(sa.text("rule_count"))]
    )
    query_str = str(query).lower().replace(os.linesep, ' ')

    assert isinstance(query, sa.sql.Select)
    assert " count(*) as rule_count" in query_str
    assert " from audit_rule" in query_str
    assert " where audit_rule.rule_id is not null" in query_str
    assert " group by audit_rule.ruleset_id" in query_str
    assert " having count(*) > :count_1" in query_str
    assert " order by rule_count desc" in query_str


async def test_build_insert_query():
    proj_name = "project-1-1-1-1-1"
    ins = bsql.build_insert(
        models.projects,
        values={"name": proj_name},
        returning=[models.projects]
    )
    ins_str = str(ins).lower().replace(os.linesep, ' ')

    assert isinstance(ins, sa.sql.Insert)
    assert " into project" in ins_str
    assert " values (:name)" in ins_str
    assert " returning project.id" in ins_str
    assert proj_name == ins._values["name"].value


async def test_execute_get_result(db: AsyncSession):
    query = bsql.build_object_query(
        models.projects,
        select_cols=[
            sa.func.count().label("prj_count"),
        ],
    )
    res = await bsql.execute_get_result(db, query)
    assert isinstance(res, sa.engine.Row)
    assert isinstance(res.prj_count, int)


async def test_execute_get_results(db: AsyncSession):
    query = bsql.build_object_query(
        models.projects,
        select_cols=[
            sa.func.count().label("prj_count"),
        ],
    )
    res = await bsql.execute_get_results(db, query)
    assert isinstance(res, sa.engine.CursorResult)


async def test_build_insert(db: AsyncSession):
    prj_name = "test-insert-001"
    query = bsql.build_insert(
        models.projects,
        values={"name": prj_name},
        returning=[models.projects],
    )
    assert isinstance(query, sa.sql.Insert)
    res = await bsql.execute_get_result(db, query)
    assert isinstance(res, sa.engine.Row)
    assert hasattr(res, "id")
    assert res.name == prj_name


async def test_insert_object_subquery(db: AsyncSession):
    prj_name = "test-ins-sel-project-002"
    cur = await bsql.insert_object(
        db,
        models.projects,
        select=bsql.build_object_query(
            select_cols=[
                sa.sql.literal(prj_name).label(models.projects.c.name.name)
            ]
        ).subquery("tmp"),
        returning=[models.projects],
    )
    assert isinstance(cur, sa.engine.CursorResult)
    res = cur.one()
    assert isinstance(res, sa.engine.Row)
    assert hasattr(res, "id")
    assert res.name == prj_name


async def test_insert_object_select(db: AsyncSession):
    await bsql.insert_object(
        db,
        models.projects,
        values=[
            {"name": "test-insert-object-select"},
            {"name": "another-test-insert-object-select"},
        ]
    )
    cur = await bsql.insert_object(
        db,
        models.projects,
        select=bsql.build_object_query(
            select_from=models.projects,
            select_cols=[
                (
                    models.projects.c.name + "|" + sa.func.cast(
                        models.projects.c.id, sa.Text
                    )
                ).label("name")
            ],
        ),
        returning=[models.projects],
    )
    assert isinstance(cur, sa.engine.CursorResult)
    res = cur.all()
    assert len(res) == cur.rowcount == 2
    for rec in res:
        assert isinstance(rec, sa.engine.Row)
        assert hasattr(rec, "id")
        assert rec.name.split('|')[-1].isdigit()
