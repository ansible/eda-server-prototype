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
