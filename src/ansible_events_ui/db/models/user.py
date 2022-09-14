from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from .base import Base

__all__ = ("User",)


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass
