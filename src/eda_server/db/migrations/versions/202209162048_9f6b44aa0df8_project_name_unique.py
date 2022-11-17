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

"""project name unique.

Revision ID: 9f6b44aa0df8
Revises: 34bca36e407d
Create Date: 2022-09-16 20:48:01.987096+00:00
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "9f6b44aa0df8"
down_revision = "34bca36e407d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(op.f("uq_project_name"), "project", ["name"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_project_name"), "project", type_="unique")
