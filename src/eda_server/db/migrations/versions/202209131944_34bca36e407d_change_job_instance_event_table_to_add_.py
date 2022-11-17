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

"""Change job instance event table to add type and timestamp.

Revision ID: 34bca36e407d
Revises: 6dab32136502
Create Date: 2022-09-13 19:44:30.295067+00:00
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "34bca36e407d"
down_revision = "6dab32136502"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "job_instance_event", sa.Column("type", sa.String(), nullable=True)
    )
    op.add_column(
        "job_instance_event",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("job_instance_event", "created_at")
    op.drop_column("job_instance_event", "type")
