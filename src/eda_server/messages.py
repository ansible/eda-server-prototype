from typing import NamedTuple

from pydantic import BaseModel


class JobEnd(NamedTuple):
    job_id: str


class ActivationErrorMessage(BaseModel):
    message: str
    detail: str
