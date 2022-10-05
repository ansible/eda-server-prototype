from typing import Optional

from pydantic import BaseModel


class JobInstance(BaseModel):
    id: Optional[int]
    playbook_id: int
    inventory_id: int
    extra_var_id: int
