import uuid
from datetime import datetime
from typing import Optional

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


class Inventory(BaseModel):
    name: StrictStr
    inventory: StrictStr
    id: Optional[int]


class Extravars(BaseModel):
    name: StrictStr
    extra_var: StrictStr
    id: Optional[int]


class Activation(BaseModel):
    id: Optional[int]
    name: StrictStr
    rulebook_id: int
    inventory_id: int
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


class Project(BaseModel):
    id: Optional[int]
    git_hash: Optional[StrictStr]
    url: StrictStr
    name: StrictStr
    description: StrictStr
    created_at: datetime = ""
    modified_at: datetime = ""

    @validator("created_at", "modified_at", pre=True, always=True)
    def set_datetime_utcnow(cls, v):
        return datetime.utcnow()


class JobInstance(BaseModel):
    id: Optional[int]
    playbook_id: int
    inventory_id: int
    extra_var_id: int


# Fast API Users


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
