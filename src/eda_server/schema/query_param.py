from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

type_schema = TypeVar("type_schema", bound=BaseModel)


class QueryParam(BaseModel):
    limit: Optional[int] = 10
    offset: Optional[int] = 10


class QueryParamPaginate(GenericModel, Generic[type_schema]):
    params: QueryParam
    data: List[type_schema]
