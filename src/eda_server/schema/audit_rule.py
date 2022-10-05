from datetime import datetime
from typing import Optional

from pydantic import BaseModel, StrictStr

from .rulebook import RuleRulesetRef


class AuditRuleActivationRef(BaseModel):
    id: int
    name: StrictStr


class AuditRule(BaseModel):
    name: StrictStr
    description: Optional[StrictStr]
    status: Optional[StrictStr]
    activation: AuditRuleActivationRef
    ruleset: RuleRulesetRef
    created_at: datetime
    fired_date: datetime
    definition: dict


class AuditRuleJobInstance(BaseModel):
    id: int
    status: Optional[StrictStr]
    last_fired_date: datetime


class AuditRuleJobInstanceEvent(BaseModel):
    id: int
    name: Optional[StrictStr]
    increment_counter: int
    type: Optional[StrictStr]
    timestamp: datetime


class AuditRuleHost(BaseModel):
    id: int
    name: Optional[StrictStr]
    status: Optional[StrictStr]
