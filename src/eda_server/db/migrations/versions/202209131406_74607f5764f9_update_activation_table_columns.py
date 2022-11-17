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

"""Update activation table columns.

Revision ID: 74607f5764f9
Revises: 93a62b2e768b
Create Date: 2022-09-13 14:06:07.046278+00:00
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "74607f5764f9"
down_revision = "93a62b2e768b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "activation",
        "activation_status",
        nullable=True,
        new_column_name="status",
    )
    op.alter_column(
        "activation",
        "activation_enabled",
        nullable=False,
        new_column_name="is_enabled",
    )
    op.alter_column(
        "activation",
        "restarted_count",
        nullable=False,
        new_column_name="restart_count",
    )


def downgrade() -> None:
    op.alter_column(
        "activation",
        "status",
        nullable=True,
        new_column_name="activation_status",
    )
    op.alter_column(
        "activation",
        "is_enabled",
        nullable=False,
        new_column_name="activation_enabled",
    )
    op.alter_column(
        "activation",
        "restart_count",
        nullable=False,
        new_column_name="restarted_count",
    )
