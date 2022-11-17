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
from typing import List, Optional

from pydantic import BaseModel, StrictStr, constr

from .extra_vars import ExtraVarsRef
from .inventory import InventoryRef
from .playbook import PlaybookRef
from .rulebook import RuleRulesetRef


def strict_not_empty_str():
    return constr(strict=True, strip_whitespace=True, min_length=1)


class ProjectCreate(BaseModel):
    url: StrictStr
    name: strict_not_empty_str()
    description: Optional[StrictStr] = ""


class ProjectRead(ProjectCreate):
    id: int
    git_hash: Optional[StrictStr]
    created_at: datetime
    modified_at: datetime


class ProjectDetail(ProjectRead):
    rulesets: List[RuleRulesetRef]
    inventories: List[InventoryRef]
    vars: List[ExtraVarsRef]
    playbooks: List[PlaybookRef]


class ProjectList(BaseModel):
    id: int
    url: StrictStr
    name: StrictStr


class ProjectUpdate(BaseModel):
    name: Optional[strict_not_empty_str()]
    description: Optional[StrictStr]
