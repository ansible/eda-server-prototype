"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}
from alembic import context

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    schema_upgrades()
    if context.get_x_argument(as_dictionary=True).get('create_default_user', None):
        data_upgrades()

def downgrade() -> None:
    ${downgrades if downgrades else "pass"}

def schema_upgrades() -> None:
    ${upgrades if upgrades else "pass"}

def data_upgrades() -> None:
    pass
