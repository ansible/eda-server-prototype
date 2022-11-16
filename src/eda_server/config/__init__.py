#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from importlib import resources
from typing import Optional

import yaml
from fastapi.requests import Request
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    secret: str = "secret"

    log_level: str = "info"

    host: str = "127.0.0.1"
    port: int = 9000

    database_url: str = (
        "postgresql+asyncpg://postgres:secret@localhost:5432/eda_server"
    )

    deployment_type: str = "docker"
    server_name: str = "localhost"

    default_user_role: Optional[str] = None

    class Config:
        env_prefix = "EDA_"
        env_nested_delimiter = "__"


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
