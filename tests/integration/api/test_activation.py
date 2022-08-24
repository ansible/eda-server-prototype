import pytest
import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db import models

TEST_ACTIVATION = {
    "id": 1,
    "name": "test-activation",
    "rulebook_id": 1,
    "inventory_id": 1,
    "extra_var_id": 1,
    "description": "demo activation",
    "execution_env_id": 1,
    "restart_policy_id": 1,
    "playbook_id": 1,
    "activation_enabled": True,
    "working_directory": "/tmp",
    "execution_environment": "quay.io/ansible/eda-project",
}

TEST_EXTRA_VAR = """
---
collections:
  - community.general
  - benthomasson.eda  # 1.3.0
"""

TEST_INVENTORY = """
---
all:
    hosts:
        localhost:
            ansible_connection: local
            ansible_python_interpreter: /usr/bin/python3
"""

TEST_RULEBOOK = """
---
- name: hello
  hosts: localhost
  gather_facts: false
  tasks:
    - debug:
        msg: hello
"""

TEST_PLAYBOOK = TEST_RULEBOOK


@pytest.mark.asyncio
async def test_create_activation(client: AsyncClient, db: AsyncSession):
    query = sa.insert(models.extra_vars).values(
        name="vars.yml", extra_var=TEST_EXTRA_VAR
    )
    await db.execute(query)
    query = sa.insert(models.inventories).values(
        name="inventory.yml", inventory=TEST_INVENTORY
    )
    await db.execute(query)
    query = sa.insert(models.rulebooks).values(
        name="ruleset.yml", rulesets=TEST_RULEBOOK
    )
    await db.execute(query)
    query = sa.insert(models.playbooks).values(
        name="hello.yml", playbook=TEST_PLAYBOOK
    )
    await db.execute(query)
    query = sa.insert(models.restart_policies).values(name="test_restart")
    await db.execute(query)
    query = sa.insert(models.execution_envs).values(
        url="quay.io/bthomass/ansible-events:latest"
    )
    await db.execute(query)

    response = await client.post(
        "/api/activations/",
        json=TEST_ACTIVATION,
    )
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == TEST_ACTIVATION["name"]

    activations = (await db.execute(sa.select(models.activations))).all()
    assert len(activations) == 1
    activation = activations[0]
    assert activation["id"] == data["id"]
    assert activation["name"] == TEST_ACTIVATION["name"]
    assert (
        activation["activation_enabled"]
        == TEST_ACTIVATION["activation_enabled"]
    )


@pytest.mark.asyncio
async def test_delete_activation_instance(
    client: AsyncClient, db: AsyncSession
):
    query = sa.insert(models.extra_vars).values(
        name="vars.yml", extra_var=TEST_EXTRA_VAR
    )
    await db.execute(query)
    extra_var = (await db.execute(sa.select(models.extra_vars))).first()

    query = sa.insert(models.inventories).values(
        name="inventory.yml", inventory=TEST_INVENTORY
    )
    await db.execute(query)
    inventory = (await db.execute(sa.select(models.inventories))).first()

    query = sa.insert(models.rulebooks).values(
        name="ruleset.yml", rulesets=TEST_RULEBOOK
    )
    await db.execute(query)
    rulebook = (await db.execute(sa.select(models.rulebooks))).first()

    query = sa.insert(models.playbooks).values(
        name="hello.yml", playbook=TEST_PLAYBOOK
    )
    await db.execute(query)

    query = sa.insert(models.activation_instances).values(
        name="test-activation",
        rulebook_id=rulebook.id,
        inventory_id=inventory.id,
        extra_var_id=extra_var.id,
    )
    await db.execute(query)

    activation_instances = (
        await db.execute(sa.select(models.activation_instances))
    ).all()
    assert len(activation_instances) == 1

    response = await client.delete("/api/activation_instance/1")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

    activations = (
        await db.execute(sa.select(models.activation_instances))
    ).all()
    assert len(activations) == 0


@pytest.mark.asyncio
async def test_create_activation_bad_entity(
    client: AsyncClient, db: AsyncSession
):
    response = await client.post(
        "/api/activations/",
        json=TEST_ACTIVATION,
    )
    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_delete_activation_not_found(client: AsyncClient):
    response = await client.delete("/api/activation_instance/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND
