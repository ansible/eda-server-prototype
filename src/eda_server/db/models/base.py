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

import sqlalchemy
from sqlalchemy.orm import declarative_base

__all__ = (
    "Base",
    "metadata",
)

NAMING_CONVENTION = {
    # Index
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    # Unique constraint
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    # Check
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    # Foreign key
    "fk": "fk_%(table_name)s_%(column_0_N_name)s",
    # Primary key
    "pk": "pk_%(table_name)s",
}
metadata = sqlalchemy.MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)
