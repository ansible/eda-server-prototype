from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, StrictStr

from eda_server.db.models.activation import (
    ExecutionEnvironment,
    RestartPolicy,
)

from .extra_vars import ExtravarsRef
from .inventory import InventoryRef
from .rulebook import RulebookRef


class ActivationCreate(BaseModel):
    name: StrictStr
    description: StrictStr = ""
    status: StrictStr = ""
    rulebook_id: int
    inventory_id: int
    restart_policy: RestartPolicy = RestartPolicy.ON_FAILURE
    is_enabled: bool = True
    extra_var_id: int = Field(None, nullable=True)
    execution_environment: ExecutionEnvironment = ExecutionEnvironment.DOCKER
    working_directory: StrictStr = ""


class ActivationBaseRead(ActivationCreate):
    id: int


class ActivationRead(BaseModel):
    id: int
    name: StrictStr
    description: StrictStr
    status: StrictStr  # TODO: will need to add enum
    is_enabled: bool
    working_directory: StrictStr
    execution_environment: ExecutionEnvironment
    rulebook: RulebookRef
    inventory: InventoryRef
    extra_var: ExtravarsRef = Field(None, nullable=True)
    restart_policy: RestartPolicy
    restarted_at: datetime = Field(None, nullable=True)
    restart_count: int
    created_at: datetime
    modified_at: datetime


class ActivationUpdate(BaseModel):
    name: StrictStr
    description: Optional[StrictStr] = ""
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
