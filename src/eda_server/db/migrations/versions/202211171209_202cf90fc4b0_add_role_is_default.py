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

"""Add is_default column to roles table.

Revision ID: 202cf90fc4b0
Revises: f592f6ef1e3a
Create Date: 2022-11-17 12:09:13.258802+00:00
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "202cf90fc4b0"
down_revision = "f592f6ef1e3a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "role",
        sa.Column(
            "is_default",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("role", "is_default")
