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

"""project table add fields.

Revision ID: c1eee0e47fc1
Revises: 11fc4f933b72
Create Date: 2022-08-31 18:23:12.353334+00:00
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c1eee0e47fc1"
down_revision = "11fc4f933b72"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("project", sa.Column("name", sa.String(), nullable=True))
    op.add_column(
        "project", sa.Column("description", sa.String(), nullable=True)
    )
    op.add_column(
        "project",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "project",
        sa.Column(
            "modified_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("project", "modified_at")
    op.drop_column("project", "created_at")
    op.drop_column("project", "description")
    op.drop_column("project", "name")
