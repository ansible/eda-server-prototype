from fastapi import APIRouter

from . import activation, auth, job, project, rulebook, task, user, websocket
from .activation import router as activation_router
from .audit_rule import router as audit_rule_router
from .job import router as job_router
from .project import router as project_router
from .rulebook import router as rulebook_router

# TODO(cutwater): Will be updated in follow up PR: Refactor routers to
#   avoid route duplication.
router = APIRouter()

router.include_router(activation_router)
router.include_router(job_router)
router.include_router(rulebook_router)
router.include_router(project_router)
router.include_router(audit_rule_router)


router.include_router(activation.router)
router.include_router(auth.router)
router.include_router(job.router)
router.include_router(project.router)
router.include_router(rulebook.router)
router.include_router(task.router)
router.include_router(user.router)
router.include_router(websocket.router)
