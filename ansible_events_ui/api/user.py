from fastapi import APIRouter

from ansible_events_ui import schema
from ansible_events_ui.users import fastapi_users

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)
router.include_router(
    fastapi_users.get_users_router(schema.UserRead, schema.UserUpdate),
)
