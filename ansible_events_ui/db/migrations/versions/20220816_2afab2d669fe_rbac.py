"""Adds user roles.

Revision ID: 2afab2d669fe
Revises: 42461b4ec88d
Create Date: 2022-08-16 08:48:58.150715

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "2afab2d669fe"
down_revision = "09d9de4b4624"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "role",
        sa.Column("id", UUID),
        sa.Column("name", sa.String),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_role")),
    )

    op.create_table(
        "action",
        sa.Column("id", UUID),
        sa.Column("name", sa.String),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_action")),
    )

    op.create_table(
        "role_action",
        sa.Column("role_id", UUID),
        sa.Column("action_id", UUID),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
            name=op.f("fk_role_action_role_role_id"),
        ),
        sa.ForeignKeyConstraint(
            ["action_id"],
            ["action.id"],
            name=op.f("fk_role_action_action_action_id"),
        ),
    )

    op.create_table(
        "user_role",
        sa.Column("role_id", UUID),
        sa.Column("user_id", UUID),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
            name=op.f("fk_user_role_role_role_id"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_user_role_user_user_id"),
        ),
    )


def downgrade() -> None:
    op.drop_table("role_action")
    op.drop_table("user_role")
    op.drop_table("role")
    op.drop_table("action")
