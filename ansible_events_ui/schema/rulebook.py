from typing import Optional

from fastapi_users import schemas
from pydantic import BaseModel, StrictStr


class Rulebook(BaseModel):
    name: StrictStr
    rulesets: StrictStr
    id: Optional[int]


class RuleRulesetRef(BaseModel):
    id: int
    name: Optional[str]


class Rule(BaseModel):
    id: int
    name: Optional[str]
    action: dict
    ruleset: RuleRulesetRef
