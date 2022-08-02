"""Add optional data seed.

Revision ID: 663ac86a4c54
Revises: 42461b4ec88d
Create Date: 2022-08-02 16:01:54.802406

"""
import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.sql import table, column
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


# revision identifiers, used by Alembic.
revision = "663ac86a4c54"
down_revision = "42461b4ec88d"
branch_labels = None
depends_on = None


def upgrade():
    schema_upgrades()
    if context.get_x_argument(as_dictionary=True).get(
        "create_default_user", None
    ):
        data_upgrades()


def downgrade():
    pass


def schema_upgrades():
    pass


def data_upgrades():
    users = table(
        "user",
        column("email", sa.String),
        column("hashed_password", sa.String),
        column("is_active", sa.Boolean),
        column("is_superuser", sa.Boolean),
        column("is_verified", sa.Boolean),
        column("id", UUID),
    )

    op.bulk_insert(
        users,
        [
            {
                "email": "admin@example.com",
                # password: "password" # noqa: E800
                "hashed_password": "$2b$12$kI9N82wfnBtawYrD4K.rvuXme"
                "/8H0Y57i9ZcVNgLgNOnSXyR5J/iu",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
                "id": str(uuid4()),
            },
        ],
    )
