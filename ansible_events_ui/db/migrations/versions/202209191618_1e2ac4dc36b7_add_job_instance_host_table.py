"""Add job_instance_host table.

Revision ID: 1e2ac4dc36b7
Revises: 9f6b44aa0df8
Create Date: 2022-09-19 16:18:22.830029+00:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "1e2ac4dc36b7"
down_revision = "9f6b44aa0df8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_instance_host",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("host", sa.String(), nullable=True),
        sa.Column("job_uuid", postgresql.UUID(), nullable=True),
        sa.Column("playbook", sa.String(), nullable=True),
        sa.Column("play", sa.String(), nullable=True),
        sa.Column("task", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_instance_host")),
    )


def downgrade() -> None:
    op.drop_table("job_instance_host")
