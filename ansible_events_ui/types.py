from enum import Enum


class ResourceType(Enum):
    PROJECT = "project"
    INVENTORY = "inventory"
    EXTRA_VAR = "extra_var"
    PLAYBOOK = "playbook"
    RULEBOOK = "rulebook"
    EXECUTION_ENV = "execution_env"
    ROLE = "role"


class Action(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
