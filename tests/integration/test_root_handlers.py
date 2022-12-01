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
from fastapi import status as status_codes
from httpx import AsyncClient


async def test_ping(client: AsyncClient):
    response = await client.get("/ping")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == {"ping": "pong!"}


async def test_openapi_yaml(client: AsyncClient):
    response = await client.get("/api/openapi.yml")
    assert response.status_code == status_codes.HTTP_200_OK
    data = yaml.safe_load(response.text)
    assert data["info"]["title"] == "Ansible Events API"
