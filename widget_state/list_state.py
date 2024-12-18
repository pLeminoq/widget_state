"""
Definition of a `ListState` which is just a list of States.
It wraps all list functions in order to causes notifications on changes to the list.
"""

from __future__ import annotations

from collections.abc import Iterator
import typing
from typing import Any, Callable, Generic, Optional, TypeVar, Union
from typing_extensions import Self

from .state import State
from .types import Serializable

if typing.TYPE_CHECKING:
    from _typeshed import SupportsDunderLT, SupportsDunderGT

T = TypeVar("T", bound=State)


class _ElementObserver:
    """
    Utility class that keeps track of all callbacks observing element-wise changes of a list state.
    """

    def __init__(self, list_state: ListState[T]) -> None:
        """
        Initialize an `_ElementObserver`.

        Parameters
        ----------
        list_state: ListState
            the list state notified by this Observer
        """
        self._callbacks: list[Callable[[State], None]] = []
        self._list_state = list_state

    def __call__(self, state: State) -> None:
        for cb in self._callbacks:
            cb(self._list_state)


class ListState(State, Generic[T]):
    """
    A list of states.
    """

    def __init__(self, _list: Optional[list[T]] = None) -> None:
        """
        Initial a `ListState`.

        Parameters
        ----------
        _list: list of State, optional
            optional pass an initial list of states
        """
        super().__init__()

        self._elem_obs = _ElementObserver(self)

        self._list: list[T] = []
        self.extend(_list if _list is not None else [])

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

    def append(self, elem: T) -> None:
        """
        Append a `State` to the list and notify.

        Parameters
        ----------
        elem: State
            the added state
        """
        self._list.append(elem)
        elem._parent = self

        elem.on_change(self._elem_obs)

        self.notify_change()

    def clear(self) -> None:
        """
        Clear the list and notify.
        """
        for elem in self._list:
            elem.remove_callback(self._elem_obs)
            elem._parent = None

        self._list.clear()

        self.notify_change()

    def extend(self, _list: list[T] | Self) -> None:
        """
        Extend the list and notify.

        Parameters
        ----------
        _list: list
            the list whose elements are added to self
        """
        # use `with` to notify just once after appending all elements
        with self:
            for elem in _list:
                self.append(elem)

    def insert(self, index: int, elem: T) -> None:
        """
        Insert an element at `index` into the list and notify.

        Parameters
        ----------
        index: int
            the position for the insertion
        elem: state
            the state inserted
        """
        self._list.insert(index, elem)
        elem._parent = self

        elem.on_change(self._elem_obs)

        self.notify_change()

    def pop(self, index: int = -1) -> State:
        """
        Pop an element at `index` from the list and notify.

        Parameters
        ----------
        index: int
            the position to remove from the list

        Returns
        -------
        State
            the remove element
        """
        elem = self._list.pop(index)
        elem._parent = None

        elem.remove_callback(self._elem_obs)

        self.notify_change()

        return elem

    def remove(self, elem: T) -> None:
        """
        Remove an element from the list and notify.

        Parameters
        ----------
        elem: State
            the state to be removed
        """
        self._list.remove(elem)
        elem._parent = None

        elem.remove_callback(self._elem_obs)

        self.notify_change()

    def reverse(self) -> None:
        """
        Reverse the list and trigger a notification.
        """
        self._list.reverse()
        self.notify_change()

    def sort(
        self, key: Callable[[T], SupportsDunderLT[Any] | SupportsDunderGT[Any]]
    ) -> None:
        """
        Wrapper to the sort method of the internal list.

        Since this method may modify the list, it triggers a
        notification.

        Parameters
        ----------
        key: callable
            function to resolve internal states into sortable values
        """
        self._list.sort(key=key)
        self.notify_change()

    def __getitem__(self, i: int) -> T:
        return self._list[i]

    def index(self, elem: T) -> int:
        """
        Wrapper to the index method of the internal list.

        Parameters
        ----------
        elem: State
            the state of which the index is retrieved

        Returns
        -------
        int
        """
        return self._list.index(elem)

    def __iter__(self) -> Iterator[T]:
        return iter(self._list)

    def __len__(self) -> int:
        return len(self._list)

    def serialize(self) -> list[Serializable]:
        return [value.serialize() for value in self]

    def deserialize(self, _list: Serializable) -> None:
        raise NotImplementedError(
            "Unable to deserialize general list state. Types of elements are unknown."
        )

    def copy_from(self, other: Self) -> None:
        assert type(self) is type(
            other
        ), f"`copy_from` needs other[type(other)] to be same type as self[{type(self)}]"

        with self:
            self.clear()
            self.extend(other)
