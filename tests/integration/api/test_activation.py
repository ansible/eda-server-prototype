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

from unittest import mock

import sqlalchemy as sa
from asyncpg_lostream.lostream import PGLargeObject
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.db.models.activation import RestartPolicy
from eda_server.db.sql import base as bsql
from eda_server.types import Action, InventorySource, ResourceType

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

TEST_ACTIVATION_INSTANCE = {
    "name": "test-activation_instance",
    "rulebook_id": 1,
    "inventory_id": 1,
    "extra_var_id": 1,
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


async def _create_activation_dependent_objects(db: AsyncSession):
    (extra_var_id,) = (
        await bsql.insert_object(
            db,
            models.extra_vars,
            values={"name": "vars.yml", "extra_var": TEST_EXTRA_VAR},
        )
    ).inserted_primary_key

    (inventory_id,) = (
        await bsql.insert_object(
            db,
            models.inventories,
            values={
                "name": "inventory.yml",
                "inventory": TEST_INVENTORY,
                "inventory_source": InventorySource.USER_DEFINED.value,
            },
        )
    ).inserted_primary_key

    (rulebook_id,) = (
        await bsql.insert_object(
            db,
            models.rulebooks,
            values={"name": "ruleset.yml", "rulesets": TEST_RULEBOOK},
        )
    ).inserted_primary_key

    (project_id,) = (
        await bsql.insert_object(
            db,
            models.projects,
            values={
                "url": "https://github.com/ansible/event-driven-ansible",
                "name": "test",
                "description": "test",
            },
        )
    ).inserted_primary_key

    foreign_keys = {
        "extra_var_id": extra_var_id,
        "inventory_id": inventory_id,
        "rulebook_id": rulebook_id,
        "project_id": project_id,
    }

    return foreign_keys


async def _create_activation(db: AsyncSession, foreign_keys: dict):
    (activation_id,) = (
        await bsql.insert_object(
            db,
            models.activations,
            values={
                "name": TEST_ACTIVATION["name"],
                "description": TEST_ACTIVATION["description"],
                "status": TEST_ACTIVATION["status"],
                "rulebook_id": foreign_keys["rulebook_id"],
                "inventory_id": foreign_keys["inventory_id"],
                "execution_environment": TEST_ACTIVATION[
                    "execution_environment"
                ],
                "working_directory": TEST_ACTIVATION["working_directory"],
                "restart_policy": TEST_ACTIVATION["restart_policy"],
                "is_enabled": TEST_ACTIVATION["is_enabled"],
                "extra_var_id": foreign_keys["extra_var_id"],
            },
        )
    ).inserted_primary_key

    return activation_id


async def test_create_activation(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    fks = await _create_activation_dependent_objects(db)
    await db.commit()

    my_test_activation = TEST_ACTIVATION.copy()
    my_test_activation["rulebook_id"] = fks["rulebook_id"]
    my_test_activation["extra_var_id"] = fks["extra_var_id"]
    my_test_activation["inventory_id"] = fks["inventory_id"]
    my_test_activation["project_id"] = fks["project_id"]

    response = await client.post(
        "/api/activations",
        json=my_test_activation,
    )
    assert response.status_code == status_codes.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == TEST_ACTIVATION["name"]

    activations = (await db.execute(sa.select(models.activations))).all()
    assert len(activations) == 1
    activation = activations[0]
    assert activation["name"] == TEST_ACTIVATION["name"]
    assert activation["is_enabled"] == TEST_ACTIVATION["is_enabled"]

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION, Action.CREATE
    )


async def test_delete_activation_instance(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    foreign_keys = await _create_activation_dependent_objects(db)

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

    # REVIEW(cutwater): This assert statement tests the test case itself
    num_activation_instances = await db.scalar(
        sa.select(func.count()).select_from(models.activation_instances)
    )
    assert num_activation_instances == 1

    await db.commit()

    response = await client.delete(f"/api/activation_instance/{inserted_id}")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

    num_activation_instances = await db.scalar(
        sa.select(func.count()).select_from(models.activation_instances)
    )
    assert num_activation_instances == 0

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION_INSTANCE, Action.DELETE
    )


async def test_ins_del_activation_instance_manages_log_lob(db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(db)
    activation_id = await _create_activation(db, foreign_keys)

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

    # REVIEW(cutwater): This query does nothing
    query = sa.delete(models.activations).where(
        models.activations.c.id == activation_id
    )


async def test_create_activation_bad_entity(client: AsyncClient):
    response = await client.post(
        "/api/activations",
        json=TEST_ACTIVATION,
    )
    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY


async def test_delete_activation_instance_not_found(client: AsyncClient):
    response = await client.delete("/api/activation_instance/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_read_activation(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    foreign_keys = await _create_activation_dependent_objects(db)
    activation_id = await _create_activation(db, foreign_keys)
    await db.commit()

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

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION, Action.READ
    )


async def test_read_activation_not_found(client: AsyncClient):
    response = await client.get("/api/activations/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_list_activations(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    foreign_keys = await _create_activation_dependent_objects(db)
    activation_id = await _create_activation(db, foreign_keys)
    await db.commit()

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

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION, Action.READ
    )


async def test_list_activations_empty_response(client: AsyncClient):
    response = await client.get(
        "/api/activations",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activations = response.json()
    assert activations == []


async def test_update_activation(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    foreign_keys = await _create_activation_dependent_objects(db)
    activation_id = await _create_activation(db, foreign_keys)
    await db.commit()

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

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION, Action.UPDATE
    )


async def test_update_activation_bad_entity(client: AsyncClient):
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


async def test_delete_activation(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    foreign_keys = await _create_activation_dependent_objects(db)
    activation_id = await _create_activation(db, foreign_keys)

    # REVIEW(cutwater): This assert statement tests the test case itself
    num_activations = await db.scalar(
        sa.select(func.count()).select_from(models.activations)
    )
    assert num_activations == 1
    await db.commit()

    response = await client.delete(f"/api/activations/{activation_id}")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

    num_activations = await db.scalar(
        sa.select(func.count()).select_from(models.activation_instances)
    )
    assert num_activations == 0

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION, Action.DELETE
    )


async def test_delete_activation_not_found(client: AsyncClient):
    response = await client.delete("/api/activations/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def _create_activation_instance(db: AsyncSession, foreign_keys: dict):
    (activation_instance_id,) = (
        await bsql.insert_object(
            db,
            models.activation_instances,
            values={
                "name": TEST_ACTIVATION_INSTANCE["name"],
                "rulebook_id": foreign_keys["rulebook_id"],
                "inventory_id": foreign_keys["inventory_id"],
                "extra_var_id": foreign_keys["extra_var_id"],
                "working_directory": TEST_ACTIVATION_INSTANCE[
                    "working_directory"
                ],
                "execution_environment": TEST_ACTIVATION_INSTANCE[
                    "execution_environment"
                ],
                "project_id": foreign_keys["project_id"],
            },
        )
    ).inserted_primary_key

    return activation_instance_id


@mock.patch("eda_server.ruleset.activate_rulesets")
async def test_create_activation_instance(
    activate_rulesets: mock.Mock,
    client: AsyncClient,
    db: AsyncSession,
    check_permission_spy: mock.Mock,
):
    fks = await _create_activation_dependent_objects(db)
    await db.commit()

    my_test_activation_instance = TEST_ACTIVATION_INSTANCE.copy()
    my_test_activation_instance["rulebook_id"] = fks["rulebook_id"]
    my_test_activation_instance["extra_var_id"] = fks["extra_var_id"]
    my_test_activation_instance["inventory_id"] = fks["inventory_id"]
    my_test_activation_instance["project_id"] = fks["project_id"]

    response = await client.post(
        "/api/activation_instance",
        json=my_test_activation_instance,
    )
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert data["name"] == TEST_ACTIVATION_INSTANCE["name"]

    activation_instances = (
        await db.execute(sa.select(models.activation_instances))
    ).all()
    assert len(activation_instances) == 1
    activation_instance = activation_instances[0]
    assert activation_instance["name"] == TEST_ACTIVATION_INSTANCE["name"]

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION_INSTANCE, Action.CREATE
    )


async def test_list_activation_instances(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    foreign_keys = await _create_activation_dependent_objects(db)
    activation_instance_id = await _create_activation_instance(
        db, foreign_keys
    )
    await db.commit()

    response = await client.get(
        "/api/activation_instances",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activation_instances = response.json()
    assert type(activation_instances) is list
    assert len(activation_instances) > 0

    activation_instance = activation_instances[0]
    assert activation_instance["id"] == activation_instance_id
    assert activation_instance["name"] == TEST_ACTIVATION_INSTANCE["name"]
    assert (
        activation_instance["working_directory"]
        == TEST_ACTIVATION_INSTANCE["working_directory"]
    )

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION_INSTANCE, Action.READ
    )


async def test_list_activation_instances_empty_response(
    client: AsyncClient, check_permission_spy: mock.Mock
):
    response = await client.get(
        "/api/activation_instances",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activation_instances = response.json()
    assert activation_instances == []

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION_INSTANCE, Action.READ
    )


async def test_read_activation_instance(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    foreign_keys = await _create_activation_dependent_objects(db)
    activation_instance_id = await _create_activation_instance(
        db, foreign_keys
    )
    await db.commit()

    response = await client.get(
        f"/api/activation_instance/{activation_instance_id}",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activation_instance = response.json()
    assert "id" in activation_instance

    assert activation_instance["name"] == TEST_ACTIVATION_INSTANCE["name"]
    assert activation_instance["id"] == activation_instance_id
    assert activation_instance["ruleset_id"] == foreign_keys["rulebook_id"]
    assert activation_instance["inventory_id"] == foreign_keys["inventory_id"]
    assert activation_instance["extra_var_id"] == foreign_keys["extra_var_id"]
    assert activation_instance["ruleset_name"] == "ruleset.yml"
    assert activation_instance["inventory_name"] == "inventory.yml"
    assert activation_instance["extra_var_name"] == "vars.yml"

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION_INSTANCE, Action.READ
    )


async def test_read_activation_instance_not_found(
    client: AsyncClient, check_permission_spy: mock.Mock
):
    response = await client.get("/api/activation_instance/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION_INSTANCE, Action.READ
    )


async def test_list_activation_instance_job_instances(
    client: AsyncClient, check_permission_spy: mock.Mock
):
    response = await client.get(
        "/api/activation_instance_job_instances/1",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activation_instance_job_instances = response.json()

    assert type(activation_instance_job_instances) is list

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION_INSTANCE, Action.READ
    )


async def test_list_activation_instance_logs(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    foreign_keys = await _create_activation_dependent_objects(db)
    instance_id = await _create_activation_instance(db, foreign_keys)
    await db.commit()

    response = await client.get(
        f"/api/activation_instance_logs?activation_instance_id={instance_id}",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activation_instance_logs = response.json()

    assert type(activation_instance_logs) is list

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION_INSTANCE, Action.READ
    )


async def test_list_activation_instance_logs_not_found(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    response = await client.get(
        "/api/activation_instance_logs?activation_instance_id=1",
    )
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ACTIVATION_INSTANCE, Action.READ
    )
