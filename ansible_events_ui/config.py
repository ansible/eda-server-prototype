from pydantic import BaseSettings


class Settings(BaseSettings):
    secret: str = "secret"

    log_level: str = "INFO"

    host: str = "127.0.0.1"
    port: int = 8080

    # FIXME(cutwater): Use only asynchronous sqlalchemy connection
    database_url: str = "sqlite:///./test.db"
    async_database_url: str = "sqlite+aiosqlite:///./test.db"

    class Config:
        env_prefix = "AE_"
        env_nested_delimiter = "__"


# TODO(cutwater): Eliminate global settings object
settings = Settings()
