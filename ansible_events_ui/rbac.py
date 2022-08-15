from sqlalchemy.ext.asyncio import AsyncSession
from .db.models import User, actions, role_actions, user_roles, roles
from sqlalchemy import select
from fastapi import HTTPException


async def query_action(db: AsyncSession, user: User, action: str):

    # fmt: off
    result = await db.execute(
        select(actions.c.id, actions.c.name)
        .select_from(
            actions.join(role_actions)
            .join(roles)
            .join(user_roles)
            .join(User)
        )
        .where(User.email == user.email, actions.c.name == action)
    )
    # fmt: on

    return result.all()


async def check_action(db: AsyncSession, user: User, action: str):

    result = await query_action(db, user, action)

    if len(result) == 0:
        raise HTTPException(status_code=401, detail="Not Authorized!")

    if len(result) == 1:
        if result[0].name != action:
            raise HTTPException(status_code=401, detail="Invalid action")

    if len(result) > 1:
        raise HTTPException(status_code=401, detail="Invalid actions")
