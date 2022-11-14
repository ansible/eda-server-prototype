from typing import Generic, List, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

type_schema = TypeVar("type_schema", bound=BaseModel)


class QueryParam(BaseModel):
    limit: int
    offset: int


class QueryParamPaginate(GenericModel, Generic[type_schema]):
    params: QueryParam
    data: List[type_schema]
