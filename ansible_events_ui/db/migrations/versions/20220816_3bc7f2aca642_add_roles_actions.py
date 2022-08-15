"""add_roles_actions.

Revision ID: 3bc7f2aca642
Revises: 2afab2d669fe
Create Date: 2022-08-16 11:01:52.510359

"""
from alembic import op
from ansible_events_ui.db.models import roles, actions, role_actions
from uuid import uuid4

# revision identifiers, used by Alembic.
revision = "3bc7f2aca642"
down_revision = "2afab2d669fe"
branch_labels = None
depends_on = None


def upgrade() -> None:

    role_names = [
        "Owner",
        "None",
        "Editor",
        "Auditor",
        "Approver",
        "Contributor",
        "Viewer",
        "Operator",
    ]

    role_data = [{"id": str(uuid4()), "name": x} for x in role_names]
    role_uuids = {x["name"]: x["id"] for x in role_data}

    op.bulk_insert(roles, role_data)

    action_names = [
        "test",
        "import project",
        "read project",
        "update project",
        "delete project",
        "import collection",
        "read collection",
        "update collection",
        "delete collection",
        "create rulebook activation",
        "read rulebook activation",
        "update rulebook activation",
        "enable rulebook activation",
        "disable rulebook activation",
        "delete rulebook activation",
        "create job instance",
        "read job instance",
        "delete job instance",
        "create rulebook",
        "read rulebook",
        "update rulebook",
        "delete rulebook",
        "create inventory",
        "read inventory",
        "update inventory",
        "delete inventory",
        "create vars",
        "read vars",
        "update vars",
        "delete vars",
        "create playbook",
        "read playbook",
        "update playbook",
        "delete playbook",
        "create role",
        "read role",
        "update role",
        "delete role",
        "create user",
        "read user",
        "update user",
        "delete user",
    ]

    action_data = [{"id": str(uuid4()), "name": x} for x in action_names]
    action_uuids = {x["name"]: x["id"] for x in action_data}
    op.bulk_insert(actions, action_data)

    owner_actions = [
        {"role_id": role_uuids["Owner"], "action_id": x}
        for x in action_uuids.values()
    ]
    op.bulk_insert(role_actions, owner_actions)


def downgrade() -> None:
    pass
