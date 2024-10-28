from __future__ import annotations

from collections.abc import Iterator
from typing import Callable, Optional, Union

from .state import State
from .types import Serializable


class _ElementObserver:
    """
    Utility class that keeps track of all callbacks observing element-wise changes of a list state.
    """

    def __init__(self, list_state: ListState) -> None:
        self._callbacks: list[Callable[[State], None]] = []
        self._list_state = list_state

    def __call__(self, state: State) -> None:
        for cb in self._callbacks:
            cb(self._list_state)


class ListState(State):

    def __init__(self, _list: list[State] = []):
        super().__init__()

        self._elem_obs = _ElementObserver(self)

        self._list: list[State] = []
        self.extend(_list)

    def on_change(
        self,
        callback: Callable[[State], None],
        trigger: bool = False,
        element_wise: bool = False,
    ) -> int:
        if element_wise:
            self._elem_obs._callbacks.append(callback)

        return super().on_change(callback, trigger=trigger)

    def remove_callback(
        self, callback_or_id: Union[Callable[[State], None], int]
    ) -> None:
        if isinstance(callback_or_id, int):
            cb = self._callbacks.pop(callback_or_id)
        else:
            self._callbacks.remove(callback_or_id)
            cb = callback_or_id

        if cb in self._elem_obs._callbacks:
            self._elem_obs._callbacks.remove(cb)

    def append(self, elem: State) -> None:
        self._list.append(elem)
        elem._parent = self

        elem.on_change(self._elem_obs)

        self.notify_change()

    def clear(self) -> None:
        for elem in self._list:
            elem.remove_callback(self._elem_obs)
            elem._parent = None

        self._list.clear()

        self.notify_change()

    def extend(self, _list: list[State]) -> None:
        # use `with` to notify just once after appending all elements
        with self:
            for elem in _list:
                self.append(elem)

    def insert(self, index: int, elem: State) -> None:
        self._list.insert(index, elem)
        elem._parent = self

        elem.on_change(self._elem_obs)

        self.notify_change()

    def pop(self, index: int = -1) -> State:
        elem = self._list.pop(index)
        elem._parent = None

        elem.remove_callback(self._elem_obs)

        self.notify_change()

        return elem

    def remove(self, elem: State) -> None:
        self._list.remove(elem)
        elem._parent = None

        elem.remove_callback(self._elem_obs)

        self.notify_change()

    def reverse(self) -> None:
        self._list.reverse()
        self.notify_change()

    def sort(
        self, key: Optional[Callable[[State], Union[str | int | float]]] = None
    ) -> None:
        self._list.sort(key=key)
        self.notify_change()

    def __getitem__(self, i: int) -> State:
        return self._list[i]

    def index(self, elem: State) -> int:
        return self._list.index(elem)

    def __iter__(self) -> Iterator[State]:
        return iter(self._list)

    def __len__(self) -> int:
        return len(self._list)

    def serialize(self) -> list[Serializable]:
        return [value.serialize() for value in self]

    def deserialize(self, _list: Serializable) -> None:
        raise NotImplementedError(
            "Unable to deserialize general list state. Types of elements are unknown."
        )
