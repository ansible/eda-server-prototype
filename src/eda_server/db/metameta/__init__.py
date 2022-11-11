from typing import Any, Hashable, List, Optional


class dicta(dict):
    """
    Dict subclass that can access values via key or attribute.

    Ex:
        x = dicta(a=1, b=2)
        print(x.a)     # 1
        print(x['b'])  # 2
    """

    def __getattr__(self, key: Hashable):
        """Get attribute."""
        return super().__getitem__(key)

    def __setattr__(self, key: Hashable, val: Any):
        """Set attribute."""
        super().__setitem__(key, val)

    def __delattr__(self, key: Hashable):
        """Delete attribute."""
        super().__delitem__(key)

    def copy(self):
        """Get a copy."""
        return self.__class__(self)


class MetaMetaBase:
    def __init__(self):
        self._items = dicta()
        self.name = "MetaMetaBase"

    def _get_child_class(self):
        return self.__class__

    def __getattr__(self, key: str) -> Any:
        if key in self._items:
            return self._items[key]
        else:
            super().__getattr__(key)

    def __contains__(self, item_name: str) -> bool:
        return item_name in self._items

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __str__(self):
        return f"{self.__repr__()}.({(s for s in self.list_item_keys())})"

    def list_item_keys(self) -> List[Any]:
        return sorted(self._items)


__all__ = ("dicta",)
