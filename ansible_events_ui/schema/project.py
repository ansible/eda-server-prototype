from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, StrictStr

from ansible_events_ui import schema


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
    rulesets: List[schema.RuleRulesetRef]
    inventories: List[schema.InventoryRef]
    vars: List[schema.ExtravarsRef]
    playbooks: List[schema.PlaybookRef]


class ProjectList(BaseModel):
    id: int
    url: StrictStr
    name: StrictStr


class ProjectUpdate(BaseModel):
    name: StrictStr
