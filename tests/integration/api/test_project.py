import pytest
import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db import models

TEST_PROJECT = {
    "url": "https://github.com/benthomasson/eda-project",
    "name": "Test Name",
    "description": "This is a test description",
}


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, db: AsyncSession):
    response = await client.post(
        "/api/new-project/",
        json=TEST_PROJECT,
    )
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == TEST_PROJECT["name"]

    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 1
    project = projects[0]
    assert project["id"] == data["id"]
    assert project["name"] == TEST_PROJECT["name"]
    assert (
        project["url"]
        == TEST_PROJECT["url"]
    )


@pytest.mark.asyncio
async def test_create_project_bad_entity(
    client: AsyncClient, db: AsyncSession
):
    bad_project = {
    "url": None,
    "name": "Test Name",
    "description": "This is a test description",
    }
    response = await client.post(
        "/api/new-project/",
        json=bad_project,
    )
    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_get_project(
    client: AsyncClient, db: AsyncSession 
    ):

    query = sa.insert(models.projects).values(
        url=TEST_PROJECT["url"], 
        name=TEST_PROJECT["name"], 
        description=TEST_PROJECT["description"],
    )

    await db.execute(query)

    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 1
    project = projects[0]
   
    response = await client.get(
        "/api/project/" + str(project["id"])
    )

    assert response.status_code == status_codes.HTTP_200_OK

    data = response.json()
    assert data["name"] == TEST_PROJECT["name"]
    assert (
        data["url"]
        == TEST_PROJECT["url"]
    )

@pytest.mark.asyncio
async def test_get_project_not_found(
    client: AsyncClient, db: AsyncSession 
    ):

    query = sa.insert(models.projects).values(
        url=TEST_PROJECT["url"], 
        name=TEST_PROJECT["name"], 
        description=TEST_PROJECT["description"],
    )

    await db.execute(query)

    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 1
    project = projects[0]
   
    response = await client.get(
        "/api/project/4"
    )

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_projects(
    client: AsyncClient, db: AsyncSession 
    ):

    test_project_two = {
        "url": "https://github.com/benthomasson/eda-project",
        "name": "Test Name TWO",
        "description": "This is a test description two",
    }

    test_projects = [TEST_PROJECT, test_project_two]

    for test_project in test_projects:
        query = sa.insert(models.projects).values(
            url=test_project["url"], 
            name=test_project["name"], 
            description=test_project["description"],
        )
        await db.execute(query)

    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 2
   
    response = await client.get(
        "/api/projects/"
    )

    assert response.status_code == status_codes.HTTP_200_OK

    data = response.json()
    assert len(data) == 2
    assert data[0]['name'] == TEST_PROJECT["name"]
    assert data[1]['url'] == test_project_two['url']

@pytest.mark.asyncio
async def test_edit_project(
    client: AsyncClient, db: AsyncSession 
    ):

    query = sa.insert(models.projects).values(
        url=TEST_PROJECT["url"], 
        name=TEST_PROJECT["name"], 
        description=TEST_PROJECT["description"],
    )

    await db.execute(query)

    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 1
    project = projects[0]
   
    response = await client.patch(
        "/api/project/" + str(project["id"]) + '/edit',
        json={"name": "new test name"},
    )

    assert response.status_code == status_codes.HTTP_200_OK

    data = response.json()
    assert data["name"] == "new test name"
