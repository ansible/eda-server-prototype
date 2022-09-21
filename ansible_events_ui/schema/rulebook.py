from datetime import datetime
from typing import Optional

from pydantic import BaseModel, StrictStr


class Rulebook(BaseModel):
    name: StrictStr
    rulesets: StrictStr
    id: Optional[int]


class RulebookRef(BaseModel):
    id: Optional[int]
    name: StrictStr


class RulesetProjectRef(BaseModel):
    id: int
    name: Optional[str]


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
    project: RulesetProjectRef


class RuleRulesetRef(BaseModel):
    id: int
    name: Optional[str]


class Rule(BaseModel):
    id: int
    name: Optional[str]
    action: dict
    ruleset: RuleRulesetRef
