from pydantic import BaseModel


class BaseParams(BaseModel):
    limit: int
    offset: int


class MetaData(BaseModel):
    params: BaseParams
