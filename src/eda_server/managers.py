#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
from collections import defaultdict

from starlette.websockets import WebSocket

logger = logging.getLogger("eda_server")


# TODO(cutwater): A more reliable, scalable and robust tasking system
#   is probably needed.
class TaskManager:
    def __init__(self):

        self.tasks = []


taskmanager = TaskManager()


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


class SecretsManager:
    def __init__(self):
        self.secrets = {}

    def set_secret(self, name, secret):
        self.secrets[name] = secret

    def get_secret(self, name):
        return self.secrets[name]

    def has_secret(self, name):
        return name in self.secrets


secretsmanager = SecretsManager()
