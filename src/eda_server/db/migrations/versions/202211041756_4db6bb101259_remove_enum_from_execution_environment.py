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

"""Remove enum from execution_environment.

Revision ID: 4db6bb101259
Revises: c703cd56f6b0
Create Date: 2022-11-04 17:56:23.742473+00:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4db6bb101259"
down_revision = "c703cd56f6b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "activation",
        "execution_environment",
        existing_type=postgresql.ENUM(
            "docker",
            "podman",
            "k8s",
            "local",
            name="execution_environment_enum",
        ),
        type_=sa.String(),
        nullable=True,
        server_default=None,
    )
    op.execute(sa.text('DROP TYPE "execution_environment_enum"'))


def downgrade() -> None:
    execution_environment = sa.Enum(
        "docker", "podman", "k8s", "local", name="execution_environment_enum"
    )
    execution_environment.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        "activation",
        "execution_environment",
        existing_type=sa.String(),
        type_=execution_environment,
        postgresql_using="execution_environment::execution_environment_enum",
        server_default=sa.text("'docker'::execution_environment_enum"),
        nullable=False,
    )
