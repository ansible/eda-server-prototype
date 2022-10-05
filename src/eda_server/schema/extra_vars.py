from typing import Optional

from pydantic import BaseModel, StrictStr


class ExtraVarsCreate(BaseModel):
    name: StrictStr
    extra_var: StrictStr


class ExtraVarsRead(ExtraVarsCreate):
    id: int


class ExtraVarsRef(BaseModel):
    name: StrictStr
    id: Optional[int]
