from typing import List

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui import schema
from ansible_events_ui.db.dependency import get_db_session
from ansible_events_ui.db.models.project import (
    extra_vars,
    inventories,
    playbooks,
    projects,
)
from ansible_events_ui.db.models.rulebook import rulebooks
from ansible_events_ui.project import clone_project, sync_project

router = APIRouter()


@router.get(
    "/api/projects/",
    response_model=List[schema.ProjectList],
    operation_id="list_projects",
    tags=["projects"],
)
async def list_projects(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(projects.c.id, projects.c.url, projects.c.name)
    result = await db.execute(query)
    return result.all()


@router.post(
    "/api/projects/",
    response_model=schema.ProjectRead,
    operation_id="create_projects",
    status_code=status.HTTP_201_CREATED,
    tags=["projects"],
)
async def create_project(
    project: schema.ProjectCreate, db: AsyncSession = Depends(get_db_session)
):
    found_hash, tempdir = await clone_project(project.url, project.git_hash)
    project.git_hash = found_hash

    query = sa.select(sa.exists().where(projects.c.name == project.name))
    project_exists = await db.scalar(query)
    if project_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{project.name}' already exists",
        )

    query = sa.insert(projects).values(
        url=project.url,
        git_hash=project.git_hash,
        name=project.name,
        description=project.description,
    )
    try:
        result = await db.execute(query)
    except sa.exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unprocessable Entity.",
        )

    (project_id,) = result.inserted_primary_key
    await sync_project(project_id, tempdir, db)
    await db.commit()

    query = sa.select(projects).where(projects.c.id == project_id)
    created_project = (await db.execute(query)).first()

    return created_project


@router.get(
    "/api/projects/{project_id}",
    response_model=schema.ProjectDetail,
    operation_id="read_project",
    tags=["projects"],
)
async def read_project(
    project_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(projects).where(projects.c.id == project_id)
    project = (await db.execute(query)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project Not Found.")

    response = dict(project)

    response["rulesets"] = (
        await db.execute(
            sa.select(rulebooks.c.id, rulebooks.c.name)
            .select_from(rulebooks)
            .join(projects)
            .where(projects.c.id == project_id)
        )
    ).all()

    response["inventories"] = (
        await db.execute(
            sa.select(inventories.c.id, inventories.c.name)
            .select_from(inventories)
            .join(projects)
            .where(projects.c.id == project_id)
        )
    ).all()

    response["vars"] = (
        await db.execute(
            sa.select(extra_vars.c.id, extra_vars.c.name)
            .select_from(extra_vars)
            .join(projects)
            .where(projects.c.id == project_id)
        )
    ).all()

    response["playbooks"] = (
        await db.execute(
            sa.select(playbooks.c.id, playbooks.c.name)
            .select_from(playbooks)
            .join(projects)
            .where(projects.c.id == project_id)
        )
    ).all()

    return response


@router.patch(
    "/api/projects/{project_id}",
    response_model=schema.ProjectRead,
    operation_id="update_project",
    tags=["projects"],
)
async def update_project(
    project_id: int,
    project: schema.ProjectUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    query = sa.select(projects).where(projects.c.id == project_id)
    stored_project = (await db.execute(query)).first()
    if not stored_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project Not Found."
        )

    query = (
        sa.update(projects)
        .where(projects.c.id == project_id)
        .values(name=project.name, description=project.description)
    )

    try:
        await db.execute(query)
    except sa.exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unprocessable Entity.",
        )

    await db.commit()

    query = sa.select(projects).where(projects.c.id == project_id)
    updated_project = (await db.execute(query)).first()

    return updated_project


@router.delete(
    "/api/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_project",
    tags=["projects"],
)
async def delete_project(
    project_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.delete(projects).where(projects.c.id == project_id)
    results = await db.execute(query)
    if results.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/api/playbooks/", tags=["playbooks"])
async def list_playbooks(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(playbooks)
    result = await db.execute(query)
    return result.all()


@router.get("/api/playbook/{playbook_id}", tags=["playbooks"])
async def read_playbook(
    playbook_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(playbooks).where(playbooks.c.id == playbook_id)
    result = (await db.execute(query)).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playbook Not Found.",
        )
    return result


@router.get("/api/inventories/", tags=["inventories"])
async def list_inventories(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(inventories)
    result = await db.execute(query)
    return result.all()


@router.get("/api/inventory/{inventory_id}", tags=["inventories"])
async def read_inventory(
    inventory_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(inventories).where(inventories.c.id == inventory_id)
    result = (await db.execute(query)).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory Not Found.",
        )
    return result


@router.post("/api/inventory/", tags=["inventories"])
async def create_inventory(
    i: schema.Inventory, db: AsyncSession = Depends(get_db_session)
):
    query = sa.insert(inventories).values(name=i.name, inventory=i.inventory)
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key
    return {**i.dict(), "id": id_}


@router.get("/api/extra_vars/", tags=["extra vars"])
async def list_extra_vars(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(extra_vars)
    result = await db.execute(query)
    return result.all()


@router.get("/api/extra_var/{extra_var_id}", tags=["extra vars"])
async def read_extravar(
    extra_var_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(extra_vars).where(extra_vars.c.id == extra_var_id)
    result = (await db.execute(query)).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extra vars Not Found.",
        )
    return result


@router.post("/api/extra_vars/", tags=["extra vars"])
async def create_extra_vars(
    e: schema.Extravars, db: AsyncSession = Depends(get_db_session)
):
    query = sa.insert(extra_vars).values(name=e.name, extra_var=e.extra_var)
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key
    return {**e.dict(), "id": id_}
