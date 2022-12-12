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

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.types import InventorySource

logger = logging.getLogger("eda_server")


async def import_inventory_file(
    db: AsyncSession, filename: str, file_content: str, project_id: int
):
    await db.execute(
        sa.insert(models.inventories).values(
            name=filename,
            inventory=file_content,
            project_id=project_id,
            inventory_source=InventorySource.PROJECT,
        )
    )


async def update_inventory(
    db: AsyncSession, file_content: str, inventory_id: int
):
    await db.execute(
        sa.update(models.inventories)
        .where(models.inventories.c.id == inventory_id)
        .values(
            inventory=file_content,
        )
    )
