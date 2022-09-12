from typing import Optional
from datetime import datetime

from pydantic import BaseModel, StrictStr


class Activation(BaseModel):
    id: Optional[int]
    name: StrictStr
    description: Optional[StrictStr]
    execution_env_id: int
    rulebook_id: int
    inventory_id: int
    restart_policy_id: int
    playbook_id: int
    activation_enabled: bool
    extra_var_id: int


class ActivationCreate(BaseModel):
    name: StrictStr
    description: Optional[StrictStr]
    rulebook_id: int
    inventory_id: int
    restart_policy_id: int
    playbook_id: int
    activation_enabled: bool
    extra_var_id: int
    working_directory: StrictStr
    execution_environment: StrictStr


class ActivationBaseRead(ActivationCreate):
    id: int


class ActivationRead(ActivationBaseRead):
    activation_status: Optional[StrictStr]
    restarted_at: Optional[datetime]
    restarted_count: int
    created_at: datetime
    modified_at: datetime
    rulebook_name: StrictStr
    inventory_name: StrictStr
    extra_var_name: StrictStr
    playbook_name: StrictStr
    restart_policy_name: StrictStr


class ActivationUpdate(BaseModel):
    name: StrictStr
    description: Optional[StrictStr]
    activation_enabled: bool


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
