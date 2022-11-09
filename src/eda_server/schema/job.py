from datetime import datetime
from typing import Optional

from pydantic import BaseModel, StrictStr


class JobInstanceCreate(BaseModel):
    id: Optional[int]
    playbook_id: int
    inventory_id: int
    extra_var_id: int


class JobInstanceBaseRead(JobInstanceCreate):
    uuid: StrictStr


class JobInstanceRead(BaseModel):
    id: int
    uuid: StrictStr
    action: Optional[StrictStr]
    name: StrictStr
    ruleset: Optional[StrictStr]
    rule: Optional[StrictStr]
    hosts: Optional[StrictStr]
    status: StrictStr
    fired_date: datetime


class JobInstanceEventsRead(BaseModel):
    id: int
    job_uuid: StrictStr
    counter: int
    stdout: StrictStr
    type: Optional[StrictStr]
    created_at: Optional[StrictStr]
