from fastapi import APIRouter, Depends

from eda_server.auth import requires_permission
from eda_server.managers import taskmanager
from eda_server.types import Action, ResourceType

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get(
    "",
    operation_id="list_tasks",
    dependencies=[
        Depends(requires_permission(ResourceType.TASK, Action.READ))
    ],
)
async def list_tasks():
    tasks = [
        {
            "name": task.get_name(),
            "done": task.done(),
            "cancelled": task.cancelled(),
        }
        for task in taskmanager.tasks
    ]
    return tasks
