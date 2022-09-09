"""Add audit rules table

Revision ID: d5f5e14c698a
Revises: c1eee0e47fc1
Create Date: 2022-09-06 19:03:44.658149+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d5f5e14c698a"
down_revision = "c1eee0e47fc1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_rule",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("fired_date", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "definition",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("rule_id", sa.Integer(), nullable=False),
        sa.Column("ruleset_id", sa.Integer(), nullable=False),
        sa.Column("activation_instance_id", sa.Integer(), nullable=False),
        sa.Column("job_instance_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activation_instance_id"],
            ["activation_instance.id"],
            name=op.f("fk_audit_rule_activation_instance_id"),
        ),
        sa.ForeignKeyConstraint(
            ["job_instance_id"],
            ["job_instance.id"],
            name=op.f("fk_audit_rule_job_instance_id"),
        ),
        sa.ForeignKeyConstraint(
            ["rule_id"], ["rule.id"], name=op.f("fk_audit_rule_rule_id")
        ),
        sa.ForeignKeyConstraint(
            ["ruleset_id"],
            ["ruleset.id"],
            name=op.f("fk_audit_rule_ruleset_id"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_rule")),
    )


def downgrade() -> None:
    op.drop_table("audit_rule")
