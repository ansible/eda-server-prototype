import pytest
import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import label

from ansible_events_ui.db import models
from ansible_events_ui.db.utils.lostream import _verify_large_object

TEST_ACTIVATION = {
    "name": "test-activation",
    "rulebook_id": 1,
    "inventory_id": 1,
    "extra_var_id": 1,
    "description": "demo activation",
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


async def _create_activation_dependent_objects(
    client: AsyncClient, db: AsyncSession
):
    (extra_var_id,) = (
        await db.execute(
            sa.insert(models.extra_vars).values(
                name="vars.yml", extra_var=TEST_EXTRA_VAR
            )
        )
    ).inserted_primary_key

    (inventory_id,) = (
        await db.execute(
            sa.insert(models.inventories).values(
                name="inventory.yml", inventory=TEST_INVENTORY
            )
        )
    ).inserted_primary_key

    (rulebook_id,) = (
        await db.execute(
            sa.insert(models.rulebooks).values(
                name="ruleset.yml", rulesets=TEST_RULEBOOK
            )
        )
    ).inserted_primary_key

    (playbook_id,) = (
        await db.execute(
            sa.insert(models.playbooks).values(
                name="hello.yml", playbook=TEST_PLAYBOOK
            )
        )
    ).inserted_primary_key

    (restart_policy_id,) = (
        await db.execute(
            sa.insert(models.restart_policies).values(name="test_restart")
        )
    ).inserted_primary_key

    foreign_keys = {
        "extra_var_id": extra_var_id,
        "inventory_id": inventory_id,
        "rulebook_id": rulebook_id,
        "playbook_id": playbook_id,
        "restart_policy_id": restart_policy_id,
    }

    return foreign_keys


async def _create_activation(
    client: AsyncClient, db: AsyncSession, foreign_keys
):
    (activation_id,) = (
        await db.execute(
            sa.insert(models.activations).values(
                name=TEST_ACTIVATION["name"],
                description=TEST_ACTIVATION["description"],
                rulebook_id=foreign_keys["rulebook_id"],
                inventory_id=foreign_keys["inventory_id"],
                execution_environment=TEST_ACTIVATION["execution_environment"],
                working_directory=TEST_ACTIVATION["working_directory"],
                restart_policy_id=foreign_keys["restart_policy_id"],
                playbook_id=foreign_keys["playbook_id"],
                activation_enabled=TEST_ACTIVATION["activation_enabled"],
                extra_var_id=foreign_keys["extra_var_id"],
            )
        )
    ).inserted_primary_key

    return activation_id


@pytest.mark.asyncio
async def test_create_activation(client: AsyncClient, db: AsyncSession):
    await _create_activation_dependent_objects(client, db)

    response = await client.post(
        "/api/activations/",
        json=TEST_ACTIVATION,
    )
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert data["name"] == TEST_ACTIVATION["name"]

    activations = (await db.execute(sa.select(models.activations))).all()
    assert len(activations) == 1
    activation = activations[0]
    assert activation["name"] == TEST_ACTIVATION["name"]
    assert (
        activation["activation_enabled"]
        == TEST_ACTIVATION["activation_enabled"]
    )


@pytest.mark.asyncio
async def test_delete_activation_instance(
    client: AsyncClient, db: AsyncSession
):
    foreign_keys = await _create_activation_dependent_objects(client, db)

    query = (
        sa.insert(models.activation_instances)
        .values(
            name="test-activation",
            rulebook_id=foreign_keys["rulebook_id"],
            inventory_id=foreign_keys["inventory_id"],
            extra_var_id=foreign_keys["extra_var_id"],
        )
        .returning(models.activation_instances.c.id)
    )
    cur = await db.execute(query)
    inserted_rows = cur.rowcount
    inserted_id = cur.first().id

    num_activation_instances = (
        (
            await db.execute(
                sa.select(label("ct", func.count())).select_from(
                    models.activation_instances
                )
            )
        )
        .first()
        .ct
    )
    assert num_activation_instances == inserted_rows == 1

    response = await client.delete(f"/api/activation_instance/{inserted_id}")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

    num_activation_instances = (
        (
            await db.execute(
                sa.select(label("ct", func.count())).select_from(
                    models.activation_instances
                )
            )
        )
        .first()
        .ct
    )
    assert num_activation_instances == 0


@pytest.mark.asyncio
async def test_ins_del_activation_instance_manages_log_lob(
    client: AsyncClient, db: AsyncSession
):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    activation_id = await _create_activation(client, db, foreign_keys)

    total_ct = existing_ct = (
        (
            await db.execute(
                sa.select(label("ct", func.count())).select_from(
                    models.activation_instances
                )
            )
        )
        .first()
        .ct
    )

    query = (
        sa.insert(models.activation_instances)
        .values(
            name="test-activation",
            rulebook_id=foreign_keys["rulebook_id"],
            inventory_id=foreign_keys["inventory_id"],
            extra_var_id=foreign_keys["extra_var_id"],
        )
        .returning(
            models.activation_instances.c.id,
            models.activation_instances.c.log_id,
        )
    )
    cur = await db.execute(query)
    inserted_rows = cur.rowcount
    inserted_id, log_id = cur.first()

    total_ct += inserted_rows
    assert total_ct == existing_ct + 1
    assert log_id is not None
    exists, _ = await _verify_large_object(log_id, db)
    assert exists

    query = sa.delete(models.activation_instances).where(
        models.activation_instances.c.id == inserted_id
    )
    cur = await db.execute(query)
    assert cur.rowcount == inserted_rows
    exists, _ = await _verify_large_object(log_id, db)
    assert not exists

    query = sa.delete(models.activations).where(
        models.activations.c.id == activation_id
    )


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


@pytest.mark.asyncio
async def test_read_activation(client: AsyncClient, db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    activation_id = await _create_activation(client, db, foreign_keys)

    response = await client.get(
        f"/api/activation/{activation_id}",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activation = response.json()
    assert "id" in activation

    assert activation["name"] == TEST_ACTIVATION["name"]
    assert activation["id"] == activation_id
    assert activation["playbook_id"] == foreign_keys["playbook_id"]
    assert (
        activation["activation_enabled"]
        == TEST_ACTIVATION["activation_enabled"]
    )


@pytest.mark.asyncio
async def test_read_activation_not_found(client: AsyncClient):
    response = await client.get("/api/activation/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_activation(client: AsyncClient, db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    activation_id = await _create_activation(client, db, foreign_keys)

    new_activation = {
        "name": "new demo",
        "description": "demo activation",
        "activation_enabled": False,
    }

    response = await client.patch(
        f"/api/activation/{activation_id}",
        json=new_activation,
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activation = response.json()

    assert activation["name"] == new_activation["name"]
    assert activation["description"] == new_activation["description"]
    assert (
        activation["activation_enabled"]
        == new_activation["activation_enabled"]
    )


@pytest.mark.asyncio
async def test_update_activation_bad_entity(
    client: AsyncClient, db: AsyncSession
):
    new_activation = {
        "name": 1,
        "description": "demo activation",
    }

    response = await client.patch(
        "/api/activation/1",
        json=new_activation,
    )
    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_update_activation_not_found(client: AsyncClient):
    new_activation = {
        "name": "new demo",
        "description": "demo activation",
        "activation_enabled": False,
    }

    response = await client.patch(
        "/api/activation/1",
        json=new_activation,
    )
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND
