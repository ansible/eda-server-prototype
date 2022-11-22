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

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, StrictStr

from eda_server.types import InventorySource


class InventoryCreate(BaseModel):
    name: StrictStr
    description: StrictStr = ""
    inventory: Optional[StrictStr] = ""
    inventory_source: InventorySource = InventorySource.USER_DEFINED


class InventoryRead(InventoryCreate):
    id: int
    project_id: Optional[int]
    created_at: datetime
    modified_at: datetime


class InventoryUpdate(BaseModel):
    name: StrictStr
    description: StrictStr = ""
    inventory: Optional[StrictStr] = ""


class InventoryRef(BaseModel):
    name: StrictStr
    id: Optional[int]
