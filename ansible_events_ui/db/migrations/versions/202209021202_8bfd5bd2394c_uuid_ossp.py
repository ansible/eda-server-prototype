"""Enable PostgreSQL uuid-ossp extension.

Revision ID: 8bfd5bd2394c
Revises: c1eee0e47fc1
Create Date: 2022-09-02 12:02:47.597045+00:00
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "8bfd5bd2394c"
down_revision = "c1eee0e47fc1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')


def downgrade() -> None:
    pass
