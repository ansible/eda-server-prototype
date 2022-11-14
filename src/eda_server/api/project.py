from typing import List, Optional

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server import schema
from eda_server.db.dependency import get_db_session
from eda_server.db.models.project import (
    extra_vars,
    inventories,
    playbooks,
    projects,
)
from eda_server.db.models.rulebook import rulebooks
from eda_server.project import GitCommandFailed, import_project

router = APIRouter()


async def project_by_name_exists_or_404(db: AsyncSession, project_name: str):
    query = sa.select(sa.exists().where(projects.c.name == project_name))
    project_exists = await db.scalar(query)
    if project_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{project_name}' already exists",
        )


@router.get(
    "/api/projects",
    operation_id="list_projects",
    response_model=schema.QueryParamPaginate[schema.ProjectList],
    tags=["projects"],
)
async def list_projects(
    db: AsyncSession = Depends(get_db_session),
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
):
    query = (
        sa.select(projects.c.id, projects.c.url, projects.c.name)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    params = {"limit": limit, "offset": offset}
    return {"params": params, "data" : result.all()}


@router.post(
    "/api/projects",
    response_model=schema.ProjectRead,
    operation_id="create_project",
    status_code=status.HTTP_201_CREATED,
    tags=["projects"],
)
async def create_project(
    data: schema.ProjectCreate, db: AsyncSession = Depends(get_db_session)
):
    # Close a transaction before the project is cloned.
    async with db.begin():
        await project_by_name_exists_or_404(db, data.name)

    async with db.begin():
        try:
            project = await import_project(db, data)
        except GitCommandFailed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot clone repository.",
            )

    return project


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
    query = sa.select(
        sa.func.count()
        .filter(projects.c.id == project_id)
        .label("project_id_count"),
        sa.func.count()
        .filter(
            sa.and_(
                projects.c.name == project.name, projects.c.id != project_id
            )
        )
        .label("project_name_count"),
    ).select_from(projects)
    exists_check = (await (db.execute(query))).one_or_none()

    if exists_check.project_id_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project Not Found."
        )

    if exists_check.project_name_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{project.name}' already exists",
        )

    values = project.dict(exclude_unset=True)
    query = (
        sa.update(projects)
        .where(projects.c.id == project_id)
        .values(**values)
        .returning(projects)
    )

    try:
        updated_project = (await db.execute(query)).one_or_none()
    except sa.exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unprocessable Entity.",
        )

    await db.commit()

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


@router.get(
    "/api/playbooks/",
    response_model=List[schema.PlaybookRead],
    operation_id="list_playbooks",
    tags=["playbooks"],
)
async def list_playbooks(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(playbooks)
    result = await db.execute(query)
    return result.all()


@router.get(
    "/api/playbook/{playbook_id}",
    response_model=schema.PlaybookRead,
    operation_id="read_playbook",
    tags=["playbooks"],
)
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


@router.get(
    "/api/inventories/",
    response_model=List[schema.InventoryRead],
    operation_id="list_inventories",
    tags=["inventories"],
)
async def list_inventories(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(inventories)
    result = await db.execute(query)
    return result.all()


@router.get(
    "/api/inventory/{inventory_id}",
    response_model=schema.InventoryRead,
    operation_id="read_inventory",
    tags=["inventories"],
)
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


@router.post(
    "/api/inventory/",
    response_model=schema.InventoryRead,
    operation_id="create_inventory",
    tags=["inventories"],
)
async def create_inventory(
    i: schema.InventoryCreate, db: AsyncSession = Depends(get_db_session)
):
    query = sa.insert(inventories).values(name=i.name, inventory=i.inventory)
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key
    return {**i.dict(), "id": id_}


@router.get(
    "/api/extra_vars/",
    response_model=List[schema.ExtraVarsRead],
    operation_id="list_extra_vars",
    tags=["extra vars"],
)
async def list_extra_vars(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(extra_vars)
    result = await db.execute(query)
    return result.all()


@router.get(
    "/api/extra_var/{extra_var_id}",
    response_model=schema.ExtraVarsRead,
    operation_id="read_extra_var",
    tags=["extra vars"],
)
async def read_extra_var(
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


@router.post(
    "/api/extra_vars/",
    response_model=schema.ExtraVarsRead,
    operation_id="create_extra_vars",
    tags=["extra vars"],
)
async def create_extra_vars(
    e: schema.ExtraVarsCreate, db: AsyncSession = Depends(get_db_session)
):
    query = sa.insert(extra_vars).values(name=e.name, extra_var=e.extra_var)
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key
    return {**e.dict(), "id": id_}
