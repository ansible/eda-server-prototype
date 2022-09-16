from datetime import datetime
from typing import Optional

from pydantic import BaseModel, StrictStr

from .extra_vars import ExtravarsRef
from .inventory import InventoryRef
from .playbook import PlaybookRef
from .rulebook import RulebookRef


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
