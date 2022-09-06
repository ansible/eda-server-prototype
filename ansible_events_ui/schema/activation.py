from typing import Optional

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


class ActivationInstance(BaseModel):
    id: Optional[int]
    name: StrictStr
    rulebook_id: int
    inventory_id: int
    extra_var_id: int


class ActivationLog(BaseModel):
    activation_instance_id: int
    log: StrictStr
    id: Optional[int]
