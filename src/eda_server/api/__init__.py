from fastapi import APIRouter

from . import (
    activation,
    audit_rule,
    auth,
    job,
    project,
    role,
    rulebook,
    task,
    user,
    ssh,
    websocket,
)

# TODO(cutwater): Will be updated in follow up PR: Refactor routers to
#   avoid route duplication.
router = APIRouter()
router.include_router(activation.router)
router.include_router(audit_rule.router)
router.include_router(auth.router)
router.include_router(job.router)
router.include_router(project.router)
router.include_router(role.router)
router.include_router(rulebook.router)
router.include_router(task.router)
router.include_router(user.router)
router.include_router(ssh.router)
router.include_router(websocket.router)
