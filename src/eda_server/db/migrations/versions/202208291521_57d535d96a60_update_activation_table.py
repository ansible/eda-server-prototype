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

"""Update activation table.

Revision ID: 57d535d96a60
Revises: 0a069266ef71
Create Date: 2022-08-29 15:21:01.782272+00:00
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "57d535d96a60"
down_revision = "0a069266ef71"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "execution_env",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("url", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_execution_env")),
    )
    op.create_table(
        "restart_policy",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_restart_policy")),
    )
    op.add_column(
        "activation", sa.Column("description", sa.String(), nullable=True)
    )
    op.add_column(
        "activation",
        sa.Column("execution_env_id", sa.Integer(), nullable=False),
    )
    op.add_column(
        "activation",
        sa.Column("restart_policy_id", sa.Integer(), nullable=False),
    )
    op.add_column(
        "activation", sa.Column("playbook_id", sa.Integer(), nullable=False)
    )
    op.add_column(
        "activation",
        sa.Column("activation_status", sa.String(), nullable=True),
    )
    op.add_column(
        "activation",
        sa.Column("activation_enabled", sa.Boolean(), nullable=False),
    )
    op.add_column(
        "activation",
        sa.Column("restarted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "activation",
        sa.Column("restarted_count", sa.Integer(), nullable=False),
    )
    op.add_column(
        "activation",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "activation",
        sa.Column(
            "modified_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
            nullable=False,
        ),
    )
    op.alter_column(
        "activation", "name", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        "activation", "rulebook_id", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "activation",
        "inventory_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    op.alter_column(
        "activation",
        "extra_var_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    op.create_foreign_key(
        op.f("fk_activation_restart_policy_id"),
        "activation",
        "restart_policy",
        ["restart_policy_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_activation_execution_env_id"),
        "activation",
        "execution_env",
        ["execution_env_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_activation_playbook_id"),
        "activation",
        "playbook",
        ["playbook_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_activation_playbook_id"), "activation", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_activation_execution_env_id"),
        "activation",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_activation_restart_policy_id"),
        "activation",
        type_="foreignkey",
    )
    op.alter_column(
        "activation", "extra_var_id", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "activation", "inventory_id", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "activation", "rulebook_id", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "activation", "name", existing_type=sa.VARCHAR(), nullable=True
    )
    op.drop_column("activation", "modified_at")
    op.drop_column("activation", "created_at")
    op.drop_column("activation", "restarted_count")
    op.drop_column("activation", "restarted_at")
    op.drop_column("activation", "activation_enabled")
    op.drop_column("activation", "activation_status")
    op.drop_column("activation", "playbook_id")
    op.drop_column("activation", "restart_policy_id")
    op.drop_column("activation", "execution_env_id")
    op.drop_column("activation", "description")
    op.drop_table("restart_policy")
    op.drop_table("execution_env")
