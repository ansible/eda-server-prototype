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

import uuid

from pydantic import BaseModel

from eda_server.types import Action, ResourceType


class RoleRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str


class RoleCreate(BaseModel):
    name: str
    description: str = ""


class RolePermissionRead(BaseModel):
    id: uuid.UUID
    resource_type: ResourceType
    action: Action


class RolePermissionCreate(BaseModel):
    resource_type: ResourceType
    action: Action
