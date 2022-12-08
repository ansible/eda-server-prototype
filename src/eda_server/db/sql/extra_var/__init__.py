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

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models


async def import_extra_var_file(
    db: AsyncSession, filename: str, file_content: str, project_id: int
):
    await db.execute(
        sa.insert(models.extra_vars).values(
            name=filename,
            extra_var=file_content,
            project_id=project_id,
        )
    )


async def update_extra_var(
    db: AsyncSession, file_content: str, extra_var_id: int
):
    await db.execute(
        sa.update(models.extra_vars)
        .where(models.extra_vars.c.id == extra_var_id)
        .values(
            extra_var=file_content,
        )
    )
