"""Initial migration.

Revision ID: 42461b4ec88d
Revises:
Create Date: 2022-07-25 14:44:36.885462

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "42461b4ec88d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "extra_var",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("extra_var", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("inventory", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "job",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "job_instance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "job_instance_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_uuid", sa.String(), nullable=True),
        sa.Column("counter", sa.Integer(), nullable=True),
        sa.Column("stdout", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "playbook",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("playbook", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("git_hash", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rule_set_file",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("rulesets", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("id", UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_table(
        "activation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("rule_set_file_id", sa.Integer(), nullable=True),
        sa.Column("inventory_id", sa.Integer(), nullable=True),
        sa.Column("extra_var_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["extra_var_id"],
            ["extra_var.id"],
        ),
        sa.ForeignKeyConstraint(
            ["inventory_id"],
            ["inventory.id"],
        ),
        sa.ForeignKeyConstraint(
            ["rule_set_file_id"],
            ["rule_set_file.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "activation_instance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("rule_set_file_id", sa.Integer(), nullable=True),
        sa.Column("inventory_id", sa.Integer(), nullable=True),
        sa.Column("extra_var_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["extra_var_id"],
            ["extra_var.id"],
        ),
        sa.ForeignKeyConstraint(
            ["inventory_id"],
            ["inventory.id"],
        ),
        sa.ForeignKeyConstraint(
            ["rule_set_file_id"],
            ["rule_set_file.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project_inventory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("inventory_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["inventory_id"],
            ["inventory.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project_playbook",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("playbook_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["playbook_id"],
            ["playbook.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project_rule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("rule_set_file_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.ForeignKeyConstraint(
            ["rule_set_file_id"],
            ["rule_set_file.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project_var",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("vars_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.ForeignKeyConstraint(
            ["vars_id"],
            ["extra_var.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "activation_instance_job_instance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("activation_instance_id", sa.Integer(), nullable=True),
        sa.Column("job_instance_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activation_instance_id"],
            ["activation_instance.id"],
        ),
        sa.ForeignKeyConstraint(
            ["job_instance_id"],
            ["job_instance.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "activation_instance_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("activation_instance_id", sa.Integer(), nullable=True),
        sa.Column("line_number", sa.Integer(), nullable=True),
        sa.Column("log", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activation_instance_id"],
            ["activation_instance.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("activation_instance_log")
    op.drop_table("activation_instance_job_instance")
    op.drop_table("project_var")
    op.drop_table("project_rule")
    op.drop_table("project_playbook")
    op.drop_table("project_inventory")
    op.drop_table("activation_instance")
    op.drop_table("activation")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
    op.drop_table("rule_set_file")
    op.drop_table("project")
    op.drop_table("playbook")
    op.drop_table("job_instance_event")
    op.drop_table("job_instance")
    op.drop_table("job")
    op.drop_table("inventory")
    op.drop_table("extra_var")
