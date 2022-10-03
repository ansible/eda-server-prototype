from typing import Optional

from pydantic import BaseModel, StrictStr


class Extravars(BaseModel):
    name: StrictStr
    extra_var: StrictStr
    id: Optional[int]


class ExtravarsRef(BaseModel):
    name: Optional[StrictStr]
    id: Optional[int]
