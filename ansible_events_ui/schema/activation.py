from datetime import datetime
from typing import Optional

from pydantic import BaseModel, StrictStr

from ansible_events_ui.db.models.activation import (
    ExecutionEnvironment,
    RestartPolicy,
)

from .extra_vars import ExtravarsRef
from .inventory import InventoryRef
from .rulebook import RulebookRef


class ActivationCreate(BaseModel):
    name: StrictStr
    description: Optional[StrictStr]
    rulebook_id: int
    inventory_id: int
    restart_policy: Optional[RestartPolicy] = RestartPolicy.ON_FAILURE
    is_enabled: Optional[bool] = True
    extra_var_id: Optional[int]
    execution_environment: Optional[
        ExecutionEnvironment
    ] = ExecutionEnvironment.DOCKER_PODMAN
    working_directory: Optional[StrictStr]


class ActivationBaseRead(ActivationCreate):
    id: int


class ActivationRead(BaseModel):
    id: int
    name: StrictStr
    description: Optional[StrictStr]
    status: Optional[StrictStr]
    is_enabled: bool
    working_directory: Optional[StrictStr]
    execution_environment: ExecutionEnvironment
    rulebook: RulebookRef
    inventory: InventoryRef
    extra_var: Optional[ExtravarsRef]
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
