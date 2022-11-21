#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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


class AuditFiredRule(BaseModel):
    id: int
    name: StrictStr
    job_id: int
    job: StrictStr
    status: Optional[StrictStr]
    ruleset_id: int
    ruleset: StrictStr
    fired_date: datetime


class AuditChangedHost(BaseModel):
    host: StrictStr
    rule_id: int
    rule: StrictStr
    ruleset_id: int
    ruleset: StrictStr
    fired_date: datetime
