from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, StrictStr
from ansible_events_ui.schema import (
    rulebook,
    extra_vars,
    inventory,
    playbook
)


class ProjectCreate(BaseModel):
    id: Optional[int]
    git_hash: Optional[StrictStr]
    url: StrictStr
    name: StrictStr
    description: StrictStr


class ProjectRead(ProjectCreate):
    created_at: datetime
    modified_at: datetime


class ProjectDetail(ProjectRead):
    rulesets: List[rulebook.RuleRulesetRef]
    inventories: List[inventory.InventoryRef]
    vars: List[extra_vars.ExtravarsRef]
    playbooks: List[playbook.PlaybookRef]


class ProjectList(BaseModel):
    id: int
    url: StrictStr
    name: StrictStr


class ProjectUpdate(BaseModel):
    name: StrictStr
