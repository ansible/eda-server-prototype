"""Change job instance event table to add type and timestamp.

Revision ID: 34bca36e407d
Revises: 6dab32136502
Create Date: 2022-09-13 19:44:30.295067+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "34bca36e407d"
down_revision = "6dab32136502"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "job_instance_event", sa.Column("type", sa.String(), nullable=True)
    )
    op.add_column(
        "job_instance_event",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("job_instance_event", "created_at")
    op.drop_column("job_instance_event", "type")
