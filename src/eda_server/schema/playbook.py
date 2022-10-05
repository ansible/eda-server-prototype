from typing import Optional

from pydantic import BaseModel, StrictStr


class PlaybookRef(BaseModel):
    id: Optional[int]
    name: StrictStr
