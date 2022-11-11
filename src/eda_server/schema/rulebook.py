from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, StrictStr


class RulebookCreate(BaseModel):
    name: StrictStr
    description: Optional[StrictStr] = ""
    rulesets: StrictStr


class RulebookRead(BaseModel):
    id: int
    name: StrictStr
    description: Optional[StrictStr]
    ruleset_count: int
    created_at: datetime
    modified_at: datetime


class RulebookRulesetList(BaseModel):
    id: int
    name: StrictStr
    rule_count: int


class RulebookList(BaseModel):
    id: int
    name: StrictStr
    ruleset_count: int


class RulebookRef(BaseModel):
    id: Optional[int]
    name: StrictStr


class RulesetProjectRef(BaseModel):
    id: int
    name: str


class FireCountsListRef(BaseModel):
    total_type: str
    status: str
    status_total: int
    object_total: int
    pct_object_total: Decimal
    window_total: int
    pct_window_total: Decimal


class FireCountsDetailRef(BaseModel):
    total_type: str
    fired_date: date
    object_status: str
    object_status_total: int
    date_status_total: int
    pct_date_status_total: Decimal
    window_total: int
    pct_window_total: Decimal


class RulesetList(BaseModel):
    id: int
    name: Optional[str]
    rule_count: int
    source_types: Optional[List[str]]
    created_at: datetime
    modified_at: datetime
    fired_stats: Optional[List[FireCountsListRef]]


class RulesetSourceRef(BaseModel):
    name: str
    type: str
    source: str
    config: dict


class RulesetSource(BaseModel):
    id: int
    name: str
    rulebook: Optional[RulebookRef]
    project: Optional[RulesetProjectRef]
    sources: Optional[List[RulesetSourceRef]]


class RulesetDetail(BaseModel):
    id: int
    name: str
    rule_count: int
    created_at: datetime
    modified_at: datetime
    sources: Optional[List[RulesetSourceRef]]
    rulebook: Optional[RulebookRef]
    project: Optional[RulesetProjectRef]
    fired_stats: Optional[List[FireCountsDetailRef]]


class RuleRef(BaseModel):
    id: int
    name: str


class RulesetRules(BaseModel):
    id: int
    name: str
    rules: List[RuleRef]


class RuleRulesetRef(BaseModel):
    id: int
    name: Optional[str]


class RuleList(BaseModel):
    id: int
    name: Optional[str]
    ruleset: RuleRulesetRef
    rulebook: Optional[RulebookRef]
    project: Optional[RulesetProjectRef]
    fired_stats: Optional[List[FireCountsListRef]]


class RuleDetail(BaseModel):
    id: int
    name: Optional[str]
    action: dict
    ruleset: RuleRulesetRef
    rulebook: Optional[RulebookRef]
    project: Optional[RulesetProjectRef]
    fired_stats: Optional[List[FireCountsDetailRef]]
