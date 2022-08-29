import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui import schemas
from ansible_events_ui.db import models
from ansible_events_ui.db.dependency import get_db_session
from ansible_events_ui.project import clone_project, sync_project

router = APIRouter()


@router.get("/api/projects/")
async def list_projects(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(
        models.projects.c.id, models.projects.c.url, models.projects.c.name
    )
    result = await db.execute(query)
    return result.all()


@router.post("/api/projects/")
async def create_project(
    p: schemas.ProjectCreate, db: AsyncSession = Depends(get_db_session)
):
    found_hash, tempdir = await clone_project(p.url, p.git_hash)
    p.git_hash = found_hash
    query = sa.insert(models.projects).values(
        url=p.url, git_hash=p.git_hash, name=p.name, description=p.description
    )
    try:
        result = await db.execute(query)
    except sa.exc.IntegrityError:
        raise HTTPException(status_code=422, detail="Unprocessable Entity.")

    (project_id,) = result.inserted_primary_key
    await sync_project(project_id, tempdir, db)
    await db.commit()
    return {**p.dict(), "id": project_id}


@router.get("/api/projects/{project_id}", response_model=schemas.ProjectRead)
async def read_project(
    project_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(models.projects).where(
        models.projects.c.id == project_id
    )
    project = (await db.execute(query)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project Not Found.")

    response = dict(project)

    response["rulesets"] = (
        await db.execute(
            sa.select(models.rulebooks.c.id, models.rulebooks.c.name)
            .select_from(models.rulebooks)
            .join(models.projects)
            .where(models.projects.c.id == project_id)
        )
    ).all()

    response["inventories"] = (
        await db.execute(
            sa.select(models.inventories.c.id, models.inventories.c.name)
            .select_from(models.inventories)
            .join(models.projects)
            .where(models.projects.c.id == project_id)
        )
    ).all()

    response["vars"] = (
        await db.execute(
            sa.select(models.extra_vars.c.id, models.extra_vars.c.name)
            .select_from(models.extra_vars)
            .join(models.projects)
            .where(models.projects.c.id == project_id)
        )
    ).all()

    response["playbooks"] = (
        await db.execute(
            sa.select(models.playbooks.c.id, models.playbooks.c.name)
            .select_from(models.playbooks)
            .join(models.projects)
            .where(models.projects.c.id == project_id)
        )
    ).all()

    return response


@router.patch("/api/projects/{project_id}")
async def read_project(
    project_id: int,
    p: schemas.ProjectUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    query = sa.select(models.projects).where(
        models.projects.c.id == project_id
    )
    stored_project = (await db.execute(query)).first()
    if not stored_project:
        raise HTTPException(status_code=404, detail="Project not found")

    query = (
        sa.update(models.projects)
        .where(models.projects.c.id == project_id)
        .values(name=p.name)
    )

    try:
        await db.execute(query)
    except sa.exc.IntegrityError:
        raise HTTPException(status_code=422, detail="Unprocessable Entity.")

    await db.commit()

    query = sa.select(models.projects).where(
        models.projects.c.id == project_id
    )
    updated_project = (await db.execute(query)).first()

    return updated_project
