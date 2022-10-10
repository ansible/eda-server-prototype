from datetime import datetime
from typing import Optional

from pydantic import BaseModel, StrictStr


class RulebookCreate(BaseModel):
    name: StrictStr
    description: Optional[StrictStr] = ""
    rulesets: StrictStr


class RulebookRead(BaseModel):
    id: int
    name: StrictStr
    description: Optional[StrictStr] = ""
    ruleset_count: int
    fire_count: int
    created_at: datetime
    modified_at: datetime

class RulebookRulesetList(BaseModel):
    id: int
    name: StrictStr
    rule_count: int
    fire_count: int


class RulebookRef(BaseModel):
    id: Optional[int]
    name: StrictStr


class RulesetProjectRef(BaseModel):
    id: int
    name: str


class Ruleset(BaseModel):
    id: int
    name: Optional[str]
    rule_count: int


class RulesetDetail(BaseModel):
    id: int
    name: Optional[str]
    rule_count: int
    created_at: datetime
    modified_at: datetime
    rulebook: RulebookRef
    project: Optional[RulesetProjectRef]


class RuleRulesetRef(BaseModel):
    id: int
    name: Optional[str]


class Rule(BaseModel):
    id: int
    name: Optional[str]
    action: dict
    ruleset: RuleRulesetRef
