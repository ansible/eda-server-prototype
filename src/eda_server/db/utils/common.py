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

import enum
from typing import List, Type


def enum_names_lower(enum_cls: Type[enum.Enum]) -> List[str]:
    """
    Return enum names in lower case.

    This function is to be used as ``values_callable`` argument
    in ``sqlalchemy.Enum`` model field types.
    """
    return [e.name.lower() for e in enum_cls]


def enum_values(enum_cls: Type[enum.Enum]) -> List[str]:
    """
    Return enum values.

    This function is to be used as ``values_callable`` argument
    in ``sqlalchemy.Enum`` model field types.

    :raises ValueError: If enum value is not a string.
    """
    values = []
    for e in enum_cls:
        if not isinstance(e.value, str):
            raise TypeError("Enum values must be strings.")
        values.append(e.value)
    return values
