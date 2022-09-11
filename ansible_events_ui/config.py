from fastapi.requests import Request
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    secret: str = "secret"

    log_level: str = "INFO"

    host: str = "127.0.0.1"
    port: int = 8080

    database_url: str = (
        "postgresql+asyncpg://postgres:secret@localhost:5432/ansible_events"
    )

    deployment_type = "docker"
    server_name = "localhost"

    class Config:
        env_prefix = "AE_"
        env_nested_delimiter = "__"


def load_settings() -> Settings:
    """Load and validate application settings."""
    return Settings()


# TODO(cutwater): Move dependencies into standalone package
def get_settings(request: Request) -> Settings:
    """Application settings dependency."""
    return request.app.state.settings
