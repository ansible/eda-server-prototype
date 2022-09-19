from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, StrictStr

from .extra_vars import ExtravarsRef
from .inventory import InventoryRef
from .playbook import PlaybookRef
from .rulebook import RuleRulesetRef


class ProjectCreate(BaseModel):
    git_hash: Optional[StrictStr]
    url: StrictStr
    name: StrictStr
    description: Optional[StrictStr] = ""


class ProjectRead(ProjectCreate):
    id: int
    created_at: datetime
    modified_at: datetime


class ProjectDetail(ProjectRead):
    rulesets: List[RuleRulesetRef]
    inventories: List[InventoryRef]
    vars: List[ExtravarsRef]
    playbooks: List[PlaybookRef]


class ProjectList(BaseModel):
    id: int
    url: StrictStr
    name: StrictStr


class ProjectUpdate(BaseModel):
    name: Optional[StrictStr]
    description: Optional[StrictStr]
