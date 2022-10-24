from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, StrictStr, constr

from .extra_vars import ExtraVarsRef
from .inventory import InventoryRef
from .meta import MetaData
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


class ProjectListWithMeta(BaseModel):
    meta: MetaData
    data: List[ProjectList]


class ProjectUpdate(BaseModel):
    name: Optional[strict_not_empty_str()]
    description: Optional[StrictStr]
