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

import argparse

import uvicorn

from .config import default_log_config, load_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--reload",
        action="store_true",
        help="Enable Auto-reload",
        default=False,
    )
    return parser.parse_args()


def main():
    settings = load_settings()
    args = parse_args()
    uvicorn.run(
        "eda_server.app:create_app",
        reload=args.reload,
        factory=True,
        host=settings.host,
        port=settings.port,
        log_config=default_log_config(),
        log_level=settings.log_level.lower(),
    )
