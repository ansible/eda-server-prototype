import sqlalchemy
from sqlalchemy.orm import declarative_base

__all__ = (
    "Base",
    "metadata",
)

NAMING_CONVENTION = {
    # Index
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    # Unique constraint
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    # Check
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    # Foreign key
    "fk": "fk_%(table_name)s_%(column_0_N_name)s",
    # Primary key
    "pk": "pk_%(table_name)s",
}
metadata = sqlalchemy.MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)
