import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui import schemas
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
    response_model=list[schemas.ProjectList],
    operation_id="list_projects",
)
async def list_projects(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(projects.c.id, projects.c.url, projects.c.name)
    result = await db.execute(query)
    return result.all()


@router.post(
    "/api/projects/",
    response_model=schemas.ProjectRead,
    operation_id="create_projects",
)
async def create_project(
    project: schemas.ProjectCreate, db: AsyncSession = Depends(get_db_session)
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
    response_model=schemas.ProjectDetail,
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
    response_model=schemas.ProjectRead,
    operation_id="update_project",
)
async def update_project(
    project_id: int,
    project: schemas.ProjectUpdate,
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


@router.delete(
    "/api/project/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_project",
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


@router.get("/api/playbooks/")
async def list_playbooks(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(playbooks)
    result = await db.execute(query)
    return result.all()


@router.get("/api/playbook/{playbook_id}")
async def read_playbook(
    playbook_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(playbooks).where(playbooks.c.id == playbook_id)
    result = await db.execute(query)
    return result.first()


@router.get("/api/inventories/")
async def list_inventories(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(inventories)
    result = await db.execute(query)
    return result.all()


@router.get("/api/inventory/{inventory_id}")
async def read_inventory(
    inventory_id: int, db: AsyncSession = Depends(get_db_session)
):
    # FIXME(cutwater): Return HTTP 404 if inventory doesn't exist
    query = sa.select(inventories).where(inventories.c.id == inventory_id)
    result = await db.execute(query)
    return result.first()


@router.post("/api/inventory/")
async def create_inventory(
    i: schemas.Inventory, db: AsyncSession = Depends(get_db_session)
):
    query = sa.insert(inventories).values(name=i.name, inventory=i.inventory)
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key
    return {**i.dict(), "id": id_}


@router.get("/api/extra_vars/")
async def list_extra_vars(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(extra_vars)
    result = await db.execute(query)
    return result.all()


@router.get("/api/extra_var/{extra_var_id}")
async def read_extravar(
    extra_var_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(extra_vars).where(extra_vars.c.id == extra_var_id)
    result = await db.execute(query)
    return result.first()


@router.post("/api/extra_vars/")
async def create_extra_vars(
    e: schemas.Extravars, db: AsyncSession = Depends(get_db_session)
):
    query = sa.insert(extra_vars).values(name=e.name, extra_var=e.extra_var)
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key
    return {**e.dict(), "id": id_}
