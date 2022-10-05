"""Enable uuid-ossp PostgreSQL extension.

Revision ID: 873701d68c86
Revises: bc14081ad342
Create Date: 2022-09-10 10:31:35.781229+00:00
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "873701d68c86"
down_revision = "bc14081ad342"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')


def downgrade() -> None:
    pass
