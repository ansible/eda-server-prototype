"""New RBAC enum values.

Revision ID: f592f6ef1e3a
Revises: c703cd56f6b0
Create Date: 2022-10-26 15:23:06.016126+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f592f6ef1e3a"
down_revision = "c703cd56f6b0"
branch_labels = None
depends_on = None


RESOURCE_TYPES = [
    "activation",
    "activation_instance",
    "audit_rule",
    "job",
    "user",
    "task",
]
ADD_RESOURCE_TYPE_QUERY = """\
ALTER TYPE "resource_type_enum" ADD VALUE IF NOT EXISTS '{value}'
"""


def upgrade() -> None:
    for value in RESOURCE_TYPES:
        op.execute(sa.text(ADD_RESOURCE_TYPE_QUERY.format(value=value)))


def downgrade() -> None:
    pass
