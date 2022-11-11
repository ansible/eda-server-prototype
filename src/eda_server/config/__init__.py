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
        return self.build_database_url(
            self.db_driver,
            self.db_user,
            self.db_password,
            self.db_host,
            self.db_port,
            self.db_name,
        )

    def build_database_url(
        self,
        driver: str,
        user: str,
        password: str,
        host: str,
        port: int,
        dbname: str,
    ) -> str:
        return (
            f"{driver}://{user}:{password}@{host}:{port}/{dbname}"
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
