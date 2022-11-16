import sqlalchemy as sa
from typing import Any, Hashable, List, Union
from .exceptions import MetaMetaNotFound

class MetaMetaBase:
    def __init__(self):
        self._items = {}
        self.name = "MetaMetaBase"
        self._notfound_exc = MetaMetaNotFound

    def __iter__(self):
        return iter(self._items)

    def __getitem__(
        self, key: str
    ) -> Union["MetaEngine", "MetaSchema", sa.Table]:
        if key not in self._items:
            raise self._notfound_exc(key)
        return self._items[key]

    def __getattr__(self, key: str) -> Any:
        if key in self._items:
            return self._items[key]
        else:
            try:
                super().__getattr__(key)
            except AttributeError:
                raise MetaMetaNotFound(key)

    def __contains__(self, item_name: str) -> bool:
        return item_name in self._items

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __str__(self) -> str:
        return f"{self.__repr__()}.({(s for s in self.list_item_keys())})"

    @property
    def child_class(self) -> "MetaMetaBase":
        NotImplementedError("The child class property must be defined")

    def keys(self):
        for key in self._items:
            yield key

    def items(self):
        for elem in self._items.items():
            yield elem

    def values(self):
        for val in self._items.values():
            yield val

    def list_item_keys(self) -> List[str]:
        return sorted(self._items)


__all__ = ("MetaMetaBase")
