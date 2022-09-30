from fastapi import APIRouter

from ansible_events_ui.managers import taskmanager

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", operation_id="list_tasks")
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
