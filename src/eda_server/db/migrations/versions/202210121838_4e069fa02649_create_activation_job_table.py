"""Create activation_job table.

Revision ID: 4e069fa02649
Revises: abfdc233b4b0
Create Date: 2022-10-12 18:38:36.657909+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4e069fa02649"
down_revision = "abfdc233b4b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "activation_job",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("activation_id", sa.Integer(), nullable=True),
        sa.Column("job_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activation_id"],
            ["activation.id"],
            name=op.f("fk_activation_job_activation_id"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["job.id"],
            name=op.f("fk_activation_job_job_id"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_activation_job")),
    )


def downgrade() -> None:
    op.drop_table("activation_job")
