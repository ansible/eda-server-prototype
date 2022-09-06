from typing import Optional

from pydantic import BaseModel, StrictStr


class Inventory(BaseModel):
    name: StrictStr
    inventory: StrictStr
    id: Optional[int]


class InventoryRef(BaseModel):
    name: StrictStr
    id: Optional[int]
