from fastapi import APIRouter

from ansible_events_ui import schema
from ansible_events_ui.users import (
    bearer_backend,
    cookie_backend,
    fastapi_users,
)

router = APIRouter()
router.include_router(
    fastapi_users.get_auth_router(cookie_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_auth_router(bearer_backend),
    prefix="/auth/bearer",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(schema.UserRead, schema.UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(schema.UserRead),
    prefix="/auth",
    tags=["auth"],
)
