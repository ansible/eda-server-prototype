from typing import Optional

from pydantic import BaseModel, StrictStr


class Rulebook(BaseModel):
    name: StrictStr
    rulesets: StrictStr
    id: Optional[int]


class RulebookRef(BaseModel):
    id: Optional[int]
    name: StrictStr


class RuleRulesetRef(BaseModel):
    id: int
    name: Optional[str]


class Rule(BaseModel):
    id: int
    name: Optional[str]
    action: dict
    ruleset: RuleRulesetRef
