import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db.dependency import get_db_session
from ansible_events_ui.db.models.project import (
    extra_vars,
    inventories,
    playbooks,
    projects,
)
from ansible_events_ui.db.models.rulebook import rulebooks
from ansible_events_ui.project import clone_project, sync_project
from ansible_events_ui.schema.project import (
    ProjectCreate,
    ProjectDetail,
    ProjectList,
    ProjectRead,
    ProjectUpdate,
)

router = APIRouter()


@router.get(
    "/api/projects/",
    response_model=list[ProjectList],
    operation_id="list_projects",
)
async def list_projects(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(projects.c.id, projects.c.url, projects.c.name)
    result = await db.execute(query)
    return result.all()


@router.post(
    "/api/projects/",
    response_model=ProjectRead,
    operation_id="create_projects",
)
async def create_project(
    project: ProjectCreate, db: AsyncSession = Depends(get_db_session)
):
    found_hash, tempdir = await clone_project(project.url, project.git_hash)
    project.git_hash = found_hash
    query = sa.insert(projects).values(
        url=project.url,
        git_hash=project.git_hash,
        name=project.name,
        description=project.description,
    )
    try:
        result = await db.execute(query)
    except sa.exc.IntegrityError:
        raise HTTPException(status_code=422, detail="Unprocessable Entity.")

    (project_id,) = result.inserted_primary_key
    await sync_project(project_id, tempdir, db)
    await db.commit()

    query = sa.select(projects).where(projects.c.id == project_id)
    created_project = (await db.execute(query)).first()

    return created_project


@router.get(
    "/api/projects/{project_id}",
    response_model=ProjectDetail,
    operation_id="read_project",
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
    response_model=ProjectRead,
    operation_id="update_project",
)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    query = sa.select(projects).where(projects.c.id == project_id)
    stored_project = (await db.execute(query)).first()
    if not stored_project:
        raise HTTPException(status_code=404, detail="Project not found")

    query = (
        sa.update(projects)
        .where(projects.c.id == project_id)
        .values(name=project.name)
    )

    try:
        await db.execute(query)
    except sa.exc.IntegrityError:
        raise HTTPException(status_code=422, detail="Unprocessable Entity.")

    await db.commit()

    query = sa.select(projects).where(projects.c.id == project_id)
    updated_project = (await db.execute(query)).first()

    return updated_project
