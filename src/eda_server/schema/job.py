from typing import Optional

from pydantic import BaseModel, StrictStr


class JobInstanceCreate(BaseModel):
    id: Optional[int]
    playbook_id: int
    inventory_id: int
    extra_var_id: int


class JobInstanceBaseRead(BaseModel):
    id: int
    uuid: StrictStr


class JobInstanceRead(JobInstanceBaseRead):
    playbook_id: int
    inventory_id: int
    extra_var_id: int


class JobInstanceEventsRead(BaseModel):
    id: int
    job_uuid: StrictStr
    counter: int
    stdout: StrictStr
    type: Optional[StrictStr]
    created_at: Optional[StrictStr]
