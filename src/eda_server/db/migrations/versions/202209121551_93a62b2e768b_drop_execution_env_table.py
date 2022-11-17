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

"""Drop execution_env table.

Revision ID: 93a62b2e768b
Revises: 61c61bfd1f7b
Create Date: 2022-09-12 15:51:02.009530+00:00
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "93a62b2e768b"
down_revision = "61c61bfd1f7b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "activation",
        sa.Column("working_directory", sa.String(), nullable=True),
    )
    op.add_column(
        "activation",
        sa.Column("execution_environment", sa.String(), nullable=True),
    )
    op.drop_constraint(
        "fk_activation_execution_env_id", "activation", type_="foreignkey"
    )
    op.drop_column("activation", "execution_env_id")
    op.drop_table("execution_env")


def downgrade() -> None:
    op.create_table(
        "execution_env",
        sa.Column(
            "id",
            sa.INTEGER(),
            sa.Identity(
                always=True,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=False,
                cache=1,
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("url", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_execution_env"),
    )
    op.add_column(
        "activation",
        sa.Column(
            "execution_env_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_activation_execution_env_id",
        "activation",
        "execution_env",
        ["execution_env_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_column("activation", "execution_environment")
    op.drop_column("activation", "working_directory")
