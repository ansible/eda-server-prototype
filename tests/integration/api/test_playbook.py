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

# TODO(cutwater): Add unit tests for API endpoints
from fastapi import status as status_codes
from httpx import AsyncClient


async def test_read_playbook_not_found(client: AsyncClient):
    response = await client.get("/api/playbook/42")

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND
