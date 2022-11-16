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

"""Add execution environment and working directory to activation instance.

Revision ID: 61c61bfd1f7b
Revises: d3abe0785cfd
Create Date: 2022-08-24 22:57:20.017549+00:00
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "61c61bfd1f7b"
down_revision = "c1eee0e47fc1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "activation_instance",
        sa.Column("execution_environment", sa.String(), nullable=True),
    )
    op.add_column(
        "activation_instance",
        sa.Column("working_directory", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("activation_instance", "execution_environment")
    op.drop_column("activation_instance", "working_directory")
