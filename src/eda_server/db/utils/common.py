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
