from typing import Optional

from pydantic import BaseModel, StrictStr


class InventoryCreate(BaseModel):
    name: StrictStr
    inventory: StrictStr


class InventoryRead(InventoryCreate):
    id: int
    project_id: Optional[int]


class InventoryRef(BaseModel):
    name: StrictStr
    id: Optional[int]
