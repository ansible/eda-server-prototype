import logging
from collections import defaultdict
from typing import List

from starlette.websockets import WebSocket

logger = logging.getLogger("ansible_events_ui")


# TODO(cutwater): A more reliable, scalable and robust tasking system
#   is probably needed.
class TaskManager:
    def __init__(self):

        self.tasks = []


taskmanager = TaskManager()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


connectionmanager = ConnectionManager()


class UpdateManager:
    def __init__(self):
        self.active_connections = defaultdict(list)

    async def connect(self, page, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[page].append(websocket)
        logger.debug("connect %s %s", page, self.active_connections[page])

    def disconnect(self, page, websocket: WebSocket):
        self.active_connections[page].remove(websocket)

    async def broadcast(self, page, message: str):
        logger.debug(
            "broadcast %s %s -> %s",
            page,
            message,
            self.active_connections[page],
        )
        for connection in self.active_connections[page]:
            await connection.send_text(message)


updatemanager = UpdateManager()
