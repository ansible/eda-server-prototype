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

"""Update inventory table.

Revision ID: 4f5d3c60fbb8
Revises: 202cf90fc4b0
Create Date: 2022-11-21 18:03:21.894162+00:00
"""

import sqlalchemy as sa
from alembic import op

import eda_server.db.utils.migrations  # noqa: F401

# revision identifiers, used by Alembic.
revision = "4f5d3c60fbb8"
down_revision = "202cf90fc4b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "inventory",
        sa.Column(
            "description", sa.String(), server_default="", nullable=True
        ),
    )
    inventory_source = sa.Enum(
        "project",
        "collection",
        "user_defined",
        "execution_env",
        name="inventory_source_enum",
    )
    inventory_source.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "inventory",
        sa.Column(
            "inventory_source",
            inventory_source,
            nullable=False,
        ),
    )
    op.add_column(
        "inventory",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "inventory",
        sa.Column(
            "modified_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.alter_column(
        "inventory", "name", existing_type=sa.VARCHAR(), nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        "inventory", "name", existing_type=sa.VARCHAR(), nullable=True
    )
    op.drop_column("inventory", "modified_at")
    op.drop_column("inventory", "created_at")
    op.drop_column("inventory", "inventory_source")
    op.drop_column("inventory", "description")
    op.drop_type("inventory_source_enum")
