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


class JobInstanceCreate(BaseModel):
    id: Optional[int]
    name: Optional[StrictStr]
    action: Optional[StrictStr]
    ruleset: Optional[StrictStr]
    rule: Optional[StrictStr]
    hosts: Optional[StrictStr]
    playbook_id: Optional[int]
    inventory_id: Optional[int]
    extra_var_id: Optional[int]


class JobInstanceBaseRead(JobInstanceCreate):
    uuid: StrictStr


class JobInstanceRead(BaseModel):
    id: int
    uuid: StrictStr
    action: Optional[StrictStr]
    name: StrictStr
    ruleset: Optional[StrictStr]
    rule: Optional[StrictStr]
    hosts: Optional[StrictStr]
    status: Optional[StrictStr]
    fired_date: Optional[datetime]


class JobInstanceEventsRead(BaseModel):
    id: int
    job_uuid: StrictStr
    counter: int
    stdout: StrictStr
    type: Optional[StrictStr]
    created_at: Optional[StrictStr]
