from http.client import HTTPException
import sqlalchemy as sa
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from ansible_events_ui.db.dependency import get_db_session
from ansible_events_ui.db.models import (
    extra_vars,
    inventories,
    playbooks,
    projects,
    rulebooks,
)
from ansible_events_ui.project import clone_project, sync_project
from ansible_events_ui.schemas import Project, ProjectUpdate

router = APIRouter()


@router.get("/api/projects/")
async def list_projects(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(projects.c.id, projects.c.url, projects.c.name)
    result = await db.execute(query)
    return result.all()


@router.post("/api/project/")
async def create_project(
    p: Project, db: AsyncSession = Depends(get_db_session)
):
    found_hash, tempdir = await clone_project(p.url, p.git_hash)
    p.git_hash = found_hash
    query = sa.insert(projects).values(
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


@router.get("/api/project/{project_id}")
async def read_project(
    project_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(projects).where(projects.c.id == project_id)
    project = (await db.execute(query)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")


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


@router.patch("/api/project/{project_id}/edit")
async def read_project(
    project_id: int, p: ProjectUpdate, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(projects).where(projects.c.id == project_id)
    stored_project = (await db.execute(query)).first()
    if not stored_project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_data = p.dict(exclude_unset=True)

    query = sa.update(projects).where(projects.c.id == project_id).values(name = project_data["name"])

    try:
        await db.execute(query)
    except sa.exc.IntegrityError:
        raise HTTPException(status_code=422, detail="Unprocessable Entity.")

    await db.commit()

    return {**p.dict()}