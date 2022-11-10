import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.db.models.activation import RestartPolicy
from eda_server.db.utils.lostream import PGLargeObject

TEST_ACTIVATION = {
    "name": "test-activation",
    "rulebook_id": 1,
    "inventory_id": 1,
    "extra_var_id": 1,
    "description": "demo activation",
    "status": "",
    "restart_policy": RestartPolicy.ON_FAILURE.value,
    "is_enabled": True,
    "working_directory": "/tmp",
    "execution_environment": "quay.io/aizquier/ansible-rulebook",
    "project_id": 1,
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

    foreign_keys = {
        "extra_var_id": extra_var_id,
        "inventory_id": inventory_id,
        "rulebook_id": rulebook_id,
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
                status=TEST_ACTIVATION["status"],
                rulebook_id=foreign_keys["rulebook_id"],
                inventory_id=foreign_keys["inventory_id"],
                execution_environment=TEST_ACTIVATION["execution_environment"],
                working_directory=TEST_ACTIVATION["working_directory"],
                restart_policy=TEST_ACTIVATION["restart_policy"],
                is_enabled=TEST_ACTIVATION["is_enabled"],
                extra_var_id=foreign_keys["extra_var_id"],
            )
        )
    ).inserted_primary_key

    return activation_id


async def test_create_activation(client: AsyncClient, db: AsyncSession):
    await _create_activation_dependent_objects(client, db)

    response = await client.post(
        "/api/activations",
        json=TEST_ACTIVATION,
    )
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert data["name"] == TEST_ACTIVATION["name"]

    activations = (await db.execute(sa.select(models.activations))).all()
    assert len(activations) == 1
    activation = activations[0]
    assert activation["name"] == TEST_ACTIVATION["name"]
    assert activation["is_enabled"] == TEST_ACTIVATION["is_enabled"]


async def test_delete_activation_instance(
    client: AsyncClient, db: AsyncSession
):
    foreign_keys = await _create_activation_dependent_objects(client, db)

    (inserted_id,) = (
        await db.execute(
            sa.insert(models.activation_instances).values(
                name="test-activation",
                rulebook_id=foreign_keys["rulebook_id"],
                inventory_id=foreign_keys["inventory_id"],
                extra_var_id=foreign_keys["extra_var_id"],
            )
        )
    ).inserted_primary_key

    num_activation_instances = await db.scalar(
        sa.select(func.count()).select_from(models.activation_instances)
    )
    assert num_activation_instances == 1

    response = await client.delete(f"/api/activation_instance/{inserted_id}")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

    num_activation_instances = await db.scalar(
        sa.select(func.count()).select_from(models.activation_instances)
    )
    assert num_activation_instances == 0


async def test_ins_del_activation_instance_manages_log_lob(
    client: AsyncClient, db: AsyncSession
):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    activation_id = await _create_activation(client, db, foreign_keys)

    total_ct = existing_ct = await db.scalar(
        sa.select(func.count()).select_from(models.activation_instances)
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
            models.activation_instances.c.large_data_id,
        )
    )
    cur = await db.execute(query)
    inserted_rows = cur.rowcount
    inserted_id, large_data_id = cur.first()

    total_ct += inserted_rows
    assert total_ct == existing_ct + 1
    assert large_data_id is not None
    exists, _ = await PGLargeObject.verify_large_object(db, large_data_id)
    assert exists

    query = sa.delete(models.activation_instances).where(
        models.activation_instances.c.id == inserted_id
    )
    cur = await db.execute(query)
    assert cur.rowcount == inserted_rows
    exists, _ = await PGLargeObject.verify_large_object(db, large_data_id)
    assert not exists

    query = sa.delete(models.activations).where(
        models.activations.c.id == activation_id
    )


async def test_create_activation_bad_entity(
    client: AsyncClient, db: AsyncSession
):
    response = await client.post(
        "/api/activations",
        json=TEST_ACTIVATION,
    )
    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY


async def test_delete_activation_instance_not_found(client: AsyncClient):
    response = await client.delete("/api/activation_instance/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_read_activation(client: AsyncClient, db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    activation_id = await _create_activation(client, db, foreign_keys)

    response = await client.get(
        f"/api/activations/{activation_id}",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activation = response.json()
    assert "id" in activation

    assert activation["name"] == TEST_ACTIVATION["name"]
    assert activation["id"] == activation_id
    assert activation["is_enabled"] == TEST_ACTIVATION["is_enabled"]
    assert (
        activation["working_directory"] == TEST_ACTIVATION["working_directory"]
    )
    assert activation["restart_policy"] == TEST_ACTIVATION["restart_policy"]
    assert (
        activation["execution_environment"]
        == TEST_ACTIVATION["execution_environment"]
    )
    assert activation["rulebook"] == {
        "id": foreign_keys["rulebook_id"],
        "name": "ruleset.yml",
    }
    assert activation["inventory"] == {
        "id": foreign_keys["inventory_id"],
        "name": "inventory.yml",
    }
    assert activation["extra_var"] == {
        "id": foreign_keys["extra_var_id"],
        "name": "vars.yml",
    }


async def test_read_activation_not_found(client: AsyncClient):
    response = await client.get("/api/activations/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_read_activations(client: AsyncClient, db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    activation_id = await _create_activation(client, db, foreign_keys)

    response = await client.get(
        "/api/activations",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activations = response.json()
    assert type(activations) is list
    assert len(activations) > 0

    activation = activations[0]
    assert activation["id"] == activation_id
    assert activation["name"] == TEST_ACTIVATION["name"]
    assert activation["description"] == TEST_ACTIVATION["description"]


async def test_read_activations_empty_response(
    client: AsyncClient, db: AsyncSession
):
    response = await client.get(
        "/api/activations",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activations = response.json()
    assert activations == []


async def test_update_activation(client: AsyncClient, db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    activation_id = await _create_activation(client, db, foreign_keys)

    new_activation = {
        "name": "new demo",
        "description": "demo activation",
        "is_enabled": False,
    }

    response = await client.patch(
        f"/api/activations/{activation_id}",
        json=new_activation,
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activation = response.json()

    assert activation["name"] == new_activation["name"]
    assert activation["description"] == new_activation["description"]
    assert activation["is_enabled"] == new_activation["is_enabled"]


async def test_update_activation_bad_entity(
    client: AsyncClient, db: AsyncSession
):
    new_activation = {
        "name": 1,
        "description": "demo activation",
    }

    response = await client.patch(
        "/api/activations/1",
        json=new_activation,
    )
    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY


async def test_update_activation_not_found(client: AsyncClient):
    new_activation = {
        "name": "new demo",
        "description": "demo activation",
        "is_enabled": False,
    }

    response = await client.patch(
        "/api/activations/1",
        json=new_activation,
    )
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_delete_activation(client: AsyncClient, db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    activation_id = await _create_activation(client, db, foreign_keys)

    num_activations = await db.scalar(
        sa.select(func.count()).select_from(models.activations)
    )
    assert num_activations == 1

    response = await client.delete(f"/api/activations/{activation_id}")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

    num_activations = await db.scalar(
        sa.select(func.count()).select_from(models.activation_instances)
    )
    assert num_activations == 0


async def test_delete_activation_not_found(client: AsyncClient):
    response = await client.delete("/api/activations/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_list_activation_instance_job_instances(
    client: AsyncClient, db: AsyncSession
):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    test_activation_instance = {
        "name": "test",
        "rulebook_id": foreign_keys["rulebook_id"],
        "inventory_id": foreign_keys["inventory_id"],
        "extra_var_id": foreign_keys["extra_var_id"],
        "working_directory": "/tmp",
        "execution_environment": "quay.io/aizquier/eda-server",
    }

    response = await client.post(
        "/api/activation_instance",
        json=test_activation_instance,
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activation_instance = response.json()
    assert "id" in activation_instance

    response = await client.get(
        f"/api/activation_instance_job_instances/{activation_instance['id']}",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activation_instance_job_instances = response.json()

    assert type(activation_instance_job_instances) is list
