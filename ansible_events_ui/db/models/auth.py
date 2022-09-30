import uuid

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql
from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from ansible_events_ui.db.utils.common import enum_values
from ansible_events_ui.types import Action, ResourceType

from .base import Base, metadata

__all__ = (
    "User",
    "roles",
    "user_roles",
    "role_permissions",
)


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass


roles = sa.Table(
    "role",
    metadata,
    sa.Column(
        "id",
        psql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("uuid_generate_v4()"),
    ),
    sa.Column(
        "name",
        sa.String,
        nullable=False,
        unique=True,
    ),
    sa.Column(
        "description",
        sa.String,
        default="",
        server_default="",
        nullable=False,
    ),
)

user_roles = sa.Table(
    "user_role",
    metadata,
    sa.Column(
        "user_id",
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "role_id",
        sa.ForeignKey("role.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.PrimaryKeyConstraint("user_id", "role_id"),
)


role_permissions = sa.Table(
    "role_permission",
    metadata,
    sa.Column(
        "id",
        psql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("uuid_generate_v4()"),
    ),
    sa.Column(
        "role_id",
        sa.ForeignKey("role.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "resource_type",
        sa.Enum(
            ResourceType,
            name="resource_type_enum",
            values_callable=enum_values,
        ),
        nullable=False,
    ),
    sa.Column(
        "action",
        sa.Enum(Action, name="action_enum", values_callable=enum_values),
        nullable=False,
    ),
    sa.UniqueConstraint("role_id", "resource_type", "action"),
)
