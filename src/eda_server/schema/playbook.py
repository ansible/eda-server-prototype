from typing import Optional

from pydantic import BaseModel, StrictStr


class PlaybookRead(BaseModel):
    id: int
    name: StrictStr
    playbook: StrictStr
    project_id: int


class PlaybookRef(BaseModel):
    id: Optional[int]
    name: StrictStr
