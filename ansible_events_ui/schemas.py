import uuid
from datetime import datetime
from typing import List, Optional

from fastapi_users import schemas
from pydantic import BaseModel, StrictStr, confloat, validator


class ProducerMessage(BaseModel):
    name: StrictStr
    message_id: StrictStr = ""
    timestamp: StrictStr = ""
    lat: confloat(gt=-90, lt=90)
    lon: confloat(gt=-180, lt=180)

    @validator("message_id", pre=True, always=True)
    def set_id_from_name_uuid(cls, v, values):
        if "name" in values:
            return f"{values['name']}_{uuid.uuid4()}"
        else:
            raise ValueError("name not set")

    @validator("timestamp", pre=True, always=True)
    def set_datetime_utcnow(cls, v):
        return str(datetime.utcnow())


class ProducerResponse(BaseModel):
    name: StrictStr
    message_id: StrictStr
    topic: StrictStr
    timestamp: StrictStr = ""

    @validator("timestamp", pre=True, always=True)
    def set_datetime_utcnow(cls, v):
        return str(datetime.utcnow())


class Rulebook(BaseModel):
    name: StrictStr
    rulesets: StrictStr
    id: Optional[int]


class RulebookRef(BaseModel):
    id: Optional[int]
    name: StrictStr


class Inventory(BaseModel):
    name: StrictStr
    inventory: StrictStr
    id: Optional[int]


class InventoryRef(BaseModel):
    name: StrictStr
    id: Optional[int]


class Extravars(BaseModel):
    name: StrictStr
    extra_var: StrictStr
    id: Optional[int]


class ExtravarsRef(BaseModel):
    name: StrictStr
    id: Optional[int]


class ActivationInstance(BaseModel):
    id: Optional[int]
    name: StrictStr
    rulebook_id: int
    inventory_id: int
    extra_var_id: int
    working_directory: StrictStr
    execution_environment: StrictStr


class ActivationLog(BaseModel):
    activation_instance_id: int
    log: StrictStr
    id: Optional[int]


class JobInstance(BaseModel):
    id: Optional[int]
    playbook_id: int
    inventory_id: int
    extra_var_id: int


class RuleRulesetRef(BaseModel):
    id: int
    name: Optional[str]


class Rule(BaseModel):
    id: int
    name: Optional[str]
    action: dict
    ruleset: RuleRulesetRef


class PlaybookRef(BaseModel):
    id: Optional[int]
    name: StrictStr


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
    name: StrictStr


class RestartPolicy(BaseModel):
    id: int
    name: StrictStr


class ActivationCreate(BaseModel):
    name: StrictStr
    description: Optional[StrictStr]
    rulebook_id: int
    inventory_id: int
    restart_policy_id: int
    playbook_id: int
    is_enabled: bool
    extra_var_id: int
    working_directory: StrictStr
    execution_environment: StrictStr


class ActivationBaseRead(ActivationCreate):
    id: int


class ActivationRead(BaseModel):
    id: int
    name: StrictStr
    description: Optional[StrictStr]
    status: Optional[StrictStr]
    is_enabled: bool
    working_directory: StrictStr
    execution_environment: StrictStr
    rulebook: RulebookRef
    inventory: InventoryRef
    extra_var: ExtravarsRef
    playbook: PlaybookRef
    restart_policy: RestartPolicy
    restarted_at: Optional[datetime]
    restart_count: int
    created_at: datetime
    modified_at: datetime


class ActivationUpdate(BaseModel):
    name: StrictStr
    description: Optional[StrictStr]
    is_enabled: bool


# Fast API Users


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
