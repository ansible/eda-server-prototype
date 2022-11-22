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

from enum import Enum


class ResourceType(Enum):
    ACTIVATION = "activation"
    ACTIVATION_INSTANCE = "activation_instance"
    AUDIT_RULE = "audit_rule"
    JOB = "job"
    TASK = "task"
    USER = "user"
    PROJECT = "project"
    INVENTORY = "inventory"
    EXTRA_VAR = "extra_var"
    PLAYBOOK = "playbook"
    RULEBOOK = "rulebook"
    EXECUTION_ENV = "execution_env"
    ROLE = "role"

    def __str__(self):
        return self.value


class Action(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"

    def __str__(self):
        return self.value


class InventorySource(Enum):
    PROJECT = "project"
    COLLECTION = "collection"
    USER_DEFINED = "user_defined"
    EXECUTION_ENV = "execution_env"
