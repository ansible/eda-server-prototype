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
