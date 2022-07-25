from pydantic import BaseSettings


class Settings(BaseSettings):
    secret: str = "secret"

    log_level: str = "INFO"

    host: str = "127.0.0.1"
    port: int = 8080

    database_url: str = (
        "postgresql+asyncpg://postgres:secret@localhost:5432/ansible_events"
    )

    class Config:
        env_prefix = "AE_"
        env_nested_delimiter = "__"


# TODO(cutwater): Eliminate global settings object
settings = Settings()
