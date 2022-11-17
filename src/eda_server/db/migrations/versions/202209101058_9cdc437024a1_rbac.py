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

"""Add RBAC tables.

Revision ID: 9cdc437024a1
Revises: 873701d68c86
Create Date: 2022-09-10 10:58:37.195873+00:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

import eda_server.db.utils.migrations  # noqa: F401

# revision identifiers, used by Alembic.
revision = "9cdc437024a1"
down_revision = "873701d68c86"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "role",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "description", sa.String(), server_default="", nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_role")),
        sa.UniqueConstraint("name", name=op.f("uq_role_name")),
    )
    op.create_table(
        "role_permission",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "resource_type",
            sa.Enum(
                "project",
                "inventory",
                "extra_var",
                "playbook",
                "rulebook",
                "execution_env",
                "role",
                name="resource_type_enum",
            ),
            nullable=False,
        ),
        sa.Column(
            "action",
            sa.Enum("create", "read", "update", "delete", name="action_enum"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
            name=op.f("fk_role_permission_role_id"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_role_permission")),
        sa.UniqueConstraint(
            "role_id",
            "resource_type",
            "action",
            name=op.f("uq_role_permission_role_id_resource_type_action"),
        ),
    )
    op.create_table(
        "user_role",
        sa.Column(
            "user_id",
            postgresql.UUID(),
            nullable=False,
        ),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
            name=op.f("fk_user_role_role_id"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_user_role_user_id"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "user_id", "role_id", name=op.f("pk_user_role")
        ),
    )


def downgrade() -> None:
    op.drop_table("user_role")
    op.drop_table("role_permission")
    op.drop_table("role")
    op.drop_type("action_enum")
    op.drop_type("resource_type_enum")
