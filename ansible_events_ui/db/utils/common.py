import enum
from typing import List, Type


def enum_values(enum_cls: Type[enum.Enum]) -> List[str]:
    values = []
    for e in enum_cls:
        if not isinstance(e.value, str):
            raise TypeError("Enum values must be strings.")
        values.append(e.value)
    return values
