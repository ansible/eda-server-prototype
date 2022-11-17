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

from sqlalchemy.ext.asyncio import create_async_engine

from eda_server.db.session import create_session_factory


class DatabaseProvider:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.session_factory = create_session_factory(self.engine)

    async def close(self) -> None:
        await self.engine.dispose()
