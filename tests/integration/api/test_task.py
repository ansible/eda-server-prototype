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

from unittest import mock

from fastapi import status as status_codes
from httpx import AsyncClient

from eda_server.types import Action, ResourceType


async def test_list_tasks(
    client: AsyncClient,
    check_permission_spy: mock.Mock,
):
    response = await client.get(
        "/api/tasks",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    tasks = response.json()

    assert tasks == []

    check_permission_spy.assert_called_with(
        mock.ANY, mock.ANY, ResourceType.TASK, Action.READ
    )
