from typing import Dict

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.db.sql import base as bsql


async def create_activation_instance(
    db: AsyncSession,
    activation_instance_rec: Dict,
) -> sa.engine.Row:

    act_inst_ins_cte = bsql.build_insert(
        models.activation_instances,
        values=activation_instance_rec,
        returning=models.activation_instances.c,
    ).cte("act_inst")

    ruleset_sources_lat = (
        sa.select(
            sa.func.array_agg(models.rulesets.c.sources).label(
                "ruleset_sources"
            )
        )
        .select_from(models.rulesets)
        .filter(
            models.rulesets.c.rulebook_id == act_inst_ins_cte.c.rulebook_id
        )
        .subquery("ruleset_sources")
        .lateral()
    )

    act_inst_query = bsql.build_object_query(
        (
            act_inst_ins_cte.join(
                models.inventories,
                act_inst_ins_cte.c.inventory_id == models.inventories.c.id,
            )
            .join(
                models.rulebooks,
                act_inst_ins_cte.c.rulebook_id == models.rulebooks.c.id,
            )
            .join(
                models.extra_vars,
                act_inst_ins_cte.c.extra_var_id == models.extra_vars.c.id,
            )
            .outerjoin(ruleset_sources_lat, sa.true())
        ),
        select_cols=[
            act_inst_ins_cte.c.id.label("activation_instance_id"),
            act_inst_ins_cte.c.large_data_id.label(
                "activation_instance_large_data_id"
            ),
            models.inventories.c.inventory,
            models.rulebooks.c.rulesets,
            sa.func.coalesce(ruleset_sources_lat.c.ruleset_sources, []).label(
                "ruleset_sources"
            ),
            models.extra_vars.c.extra_var,
        ],
    )

    activation_instance_data = await bsql.execute_get_result(
        db, act_inst_query
    )
    return activation_instance_data
