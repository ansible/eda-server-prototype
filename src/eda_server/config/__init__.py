from importlib import resources
from typing import List, Optional

import yaml
from fastapi.requests import Request
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    secret: str = "secret"

    log_level: str = "info"

    host: str = "127.0.0.1"
    port: int = 9000

    db_driver: str = "postgresql+asyncpg"
    db_user: str = "postgres"
    db_password: str = "secret"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "eda_server"

    deployment_type: str = "docker"
    server_name: str = "localhost"

    default_user_role: Optional[str] = None

    class Config:
        env_prefix = "EDA_"
        env_nested_delimiter = "__"

    @property
    def database_url(self) -> str:
        return self.build_database_url()

    def build_database_url(
        self,
        driver: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        dbname: Optional[str] = None,
    ) -> str:
        _driver = driver or self.db_driver
        _user = user or self.db_user
        _password = password or self.db_password
        _host = host or self.db_host
        _port = port or self.db_port
        _dbname = dbname or self.db_name
        return (
            f"{_driver}://{_user}:{_password}@{_host}:{_port}/{_dbname}"
        )


def load_settings() -> Settings:
    """Load and validate application settings."""
    return Settings()


def default_log_config():
    with resources.open_text(__name__, "logging.yaml") as fp:
        return yaml.safe_load(fp)


# TODO(cutwater): Drop in favor of dependency_overrides
def get_settings(request: Request) -> Settings:
    """Application settings dependency."""
    return request.app.state.settings
