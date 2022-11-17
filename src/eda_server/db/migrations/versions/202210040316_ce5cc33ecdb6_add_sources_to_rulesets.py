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

"""Add sources to rulesets.

Revision ID: ce5cc33ecdb6
Revises: 25bcfbe12475
Create Date: 2022-10-04 03:16:38.154189+00:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "ce5cc33ecdb6"
down_revision = "a6c32c91ee3f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ruleset",
        sa.Column(
            "sources",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            nullable=True,
            comment="Expanded source information from ruleset data.",
        ),
    )


def downgrade() -> None:
    op.drop_column("ruleset", "sources")
