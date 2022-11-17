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

"""Add job_instance_host table.

Revision ID: d4df045eb3ce
Revises: 1285eea03d23
Create Date: 2022-09-22 14:49:17.873228+00:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d4df045eb3ce"
down_revision = "1285eea03d23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_instance_host",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("host", sa.String(), nullable=True),
        sa.Column("job_uuid", postgresql.UUID(), nullable=True),
        sa.Column("playbook", sa.String(), nullable=True),
        sa.Column("play", sa.String(), nullable=True),
        sa.Column("task", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_instance_host")),
    )


def downgrade() -> None:
    op.drop_table("job_instance_host")
