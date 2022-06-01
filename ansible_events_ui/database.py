
from .models import metadata
import databases
import sqlalchemy

DATABASE_URL = "sqlite:///./test.db"

database = databases.Database(DATABASE_URL)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)
