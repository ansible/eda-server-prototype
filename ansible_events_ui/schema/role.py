import uuid

from pydantic import BaseModel

from ansible_events_ui.types import Action, ResourceType


class RoleRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str


class RoleCreate(BaseModel):
    name: str
    description: str = ""


class RolePermissionRead(BaseModel):
    id: uuid.UUID
    resource_type: ResourceType
    action: Action


class RolePermissionCreate(BaseModel):
    resource_type: ResourceType
    action: Action
