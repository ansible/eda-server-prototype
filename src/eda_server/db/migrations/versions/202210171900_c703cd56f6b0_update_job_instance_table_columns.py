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

"""Update job_instance table columns.

Revision ID: c703cd56f6b0
Revises: abfdc233b4b0
Create Date: 2022-10-17 19:00:22.804697+00:00
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c703cd56f6b0"
down_revision = "abfdc233b4b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "job_instance", sa.Column("action", sa.String(), nullable=True)
    )
    op.add_column(
        "job_instance", sa.Column("name", sa.String(), nullable=True)
    )
    op.add_column(
        "job_instance", sa.Column("ruleset", sa.String(), nullable=True)
    )
    op.add_column(
        "job_instance", sa.Column("rule", sa.String(), nullable=True)
    )
    op.add_column(
        "job_instance", sa.Column("hosts", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("job_instance", "hosts")
    op.drop_column("job_instance", "rule")
    op.drop_column("job_instance", "ruleset")
    op.drop_column("job_instance", "name")
    op.drop_column("job_instance", "action")
