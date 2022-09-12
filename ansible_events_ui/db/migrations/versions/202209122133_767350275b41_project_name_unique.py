"""project name unique.

Revision ID: 767350275b41
Revises: 93a62b2e768b
Create Date: 2022-09-12 21:33:16.509224+00:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "767350275b41"
down_revision = "93a62b2e768b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(op.f("uq_project_name"), "project", ["name"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_project_name"), "project", type_="unique")
