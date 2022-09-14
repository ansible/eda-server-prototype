"""project name unique.

Revision ID: 61f57495c371
Revises: 34bca36e407d
Create Date: 2022-09-14 18:33:42.937103+00:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "61f57495c371"
down_revision = "34bca36e407d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(op.f("uq_project_name"), "project", ["name"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_project_name"), "project", type_="unique")
