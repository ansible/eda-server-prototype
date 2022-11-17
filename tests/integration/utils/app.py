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

import contextlib
from typing import Any, Callable, Dict

from fastapi import FastAPI

from eda_server.app import setup_cors, setup_routes
from eda_server.db.dependency import get_db_session_factory


async def create_test_app(settings, session):
    app = FastAPI(title="Ansible Events API")
    app.state.settings = settings

    setup_cors(app)
    setup_routes(app)

    app.dependency_overrides[get_db_session_factory] = lambda: lambda: session

    return app


@contextlib.contextmanager
def override_dependencies(
    app: FastAPI,
    dependency_overrides: Dict[Callable[..., Any], Callable[..., Any]],
):
    existing_dependencies = app.dependency_overrides
    app.dependency_overrides = {
        **existing_dependencies,
        **dependency_overrides,
    }
    try:
        yield
    finally:
        app.dependency_overrides = existing_dependencies
