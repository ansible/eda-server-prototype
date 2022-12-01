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

import yaml
from fastapi import APIRouter, Request, Response

from . import (
    activation,
    audit_rule,
    auth,
    inventory,
    job,
    project,
    role,
    rulebook,
    ssh,
    task,
    user,
    websocket,
)

# TODO(cutwater): Will be updated in follow up PR: Refactor routers to
#   avoid route duplication.
router = APIRouter()
router.include_router(activation.router)
router.include_router(audit_rule.router)
router.include_router(auth.router)
router.include_router(inventory.router)
router.include_router(job.router)
router.include_router(project.router)
router.include_router(role.router)
router.include_router(rulebook.router)
router.include_router(task.router)
router.include_router(user.router)
router.include_router(ssh.router)
router.include_router(websocket.router)


OPENAPI_YAML_CACHE = None


@router.get("/api/openapi.yml", include_in_schema=False)
async def openapi_yaml(request: Request) -> Response:
    global OPENAPI_YAML_CACHE
    if OPENAPI_YAML_CACHE is None:
        OPENAPI_YAML_CACHE = yaml.dump(request.app.openapi())

    return Response(OPENAPI_YAML_CACHE, media_type="text/yaml")
