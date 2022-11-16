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

"""Use native PostgreSQL UUID type.

Revision ID: 2425525e8124
Revises: 3412abd6396d
Create Date: 2022-08-16 14:11:36.307266
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2425525e8124"
down_revision = "3412abd6396d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "job",
        "uuid",
        type_=postgresql.UUID(as_uuid=False),
        postgresql_using="uuid::uuid",
    )
    op.alter_column(
        "job_instance",
        "uuid",
        type_=postgresql.UUID(as_uuid=False),
        postgresql_using="uuid::uuid",
    )
    op.alter_column(
        "job_instance_event",
        "job_uuid",
        type_=postgresql.UUID(as_uuid=False),
        postgresql_using="job_uuid::uuid",
    )


def downgrade() -> None:
    op.alter_column("job", "uuid", type_=sa.String())
    op.alter_column("job_instance", "uuid", type_=sa.String())
    op.alter_column("job_instance_event", "job_uuid", type_=sa.String())
