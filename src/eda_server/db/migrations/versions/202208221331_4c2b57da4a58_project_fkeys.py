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

"""Refactor project relationships.

Replace many-to-many relationship with many-to-one for the following table:
  * extra_var
  * inventory
  * rule_set_file
  * playbook

Revision ID: 4c2b57da4a58
Revises: 2425525e8124
Create Date: 2022-08-22 13:31:52.240741+00:00
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4c2b57da4a58"
down_revision = "2425525e8124"
branch_labels = None
depends_on = None


def upgrade() -> None:
    upgrade_project_id_fk(
        table="extra_var",
        junction_table="project_var",
        table_ref="vars_id",
    )
    upgrade_project_id_fk(
        table="inventory",
        junction_table="project_inventory",
        table_ref="inventory_id",
    )
    upgrade_project_id_fk(
        table="rule_set_file",
        junction_table="project_rule",
        table_ref="rule_set_file_id",
    )
    upgrade_project_id_fk(
        table="playbook",
        junction_table="project_playbook",
        table_ref="playbook_id",
    )


def downgrade() -> None:
    downgrade_project_id_fk(
        table="playbook",
        junction_table="project_playbook",
        table_ref="playbook_id",
    )
    downgrade_project_id_fk(
        table="rule_set_file",
        junction_table="project_rule",
        table_ref="rule_set_file_id",
    )
    downgrade_project_id_fk(
        table="inventory",
        junction_table="project_inventory",
        table_ref="inventory_id",
    )
    downgrade_project_id_fk(
        table="extra_var",
        junction_table="project_var",
        table_ref="vars_id",
    )


def upgrade_project_id_fk(table, junction_table, table_ref):
    op.add_column(table, sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f(f"fk_{table}_project_id"),
        table,
        "project",
        ["project_id"],
        ["id"],
    )
    query = f"""
        UPDATE {table} SET project_id = {junction_table}.project_id
        FROM {junction_table}
        WHERE {table}.id = {junction_table}.{table_ref}
    """
    op.execute(sa.text(query))
    op.drop_table(junction_table)


def downgrade_project_id_fk(table, junction_table, table_ref):
    op.create_table(
        junction_table,
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column(table_ref, sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            [table_ref],
            [f"{table}.id"],
            name=f"fk_{junction_table}_{table_ref}",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
            name=f"fk_{junction_table}_project_id",
        ),
        sa.PrimaryKeyConstraint("id", name=f"pk_{junction_table}"),
    )
    query = f"""
        INSERT INTO {junction_table} (project_id, {table_ref})
        SELECT {table}.project_id, {table}.id
        FROM {table}
        WHERE {table}.project_id IS NOT NULL
    """
    op.execute(sa.text(query))
    op.drop_constraint(
        op.f(f"fk_{table}_project_id"), table, type_="foreignkey"
    )
    op.drop_column(table, "project_id")
