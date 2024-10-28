"""
Module containing the definition of the `DictState`.
A higher order state that contains only basic states as child states.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Union

from .basic_state import BasicState
from .higher_order_state import HigherOrderState
from .types import Primitive


class DictState(HigherOrderState):
    """
    A dict state is a utility state - a higher state that only contains basic states.

    It enables iteration, access by index and other utility functions.
    """

    def __init__(self, _dict: dict[str, Union[BasicState, Primitive]]) -> None:
        """
        Initialize a sequence state.

        Parameters
        ----------
        _dict: dict of basic states or primitives
            mapping from label to value
        """
        super().__init__()
        self._labels = list(_dict.keys())
        print(self._labels)

        for label, value in _dict.items():
            setattr(self, label, value)

    def __getitem__(self, i: int) -> BasicState:
        item = self.__getattribute__(self._labels[i])
        assert isinstance(item, BasicState)
        return item

    def __iter__(self) -> Iterator[BasicState]:
        return iter(map(self.__getattribute__, self._labels))

    def __len__(self) -> int:
        return len(self._labels)

    def values(self) -> list[Any]:
        """
        Get the values of all internal states as a list.
        """
        return [attr.value for attr in self]

    def set(self, *args: BasicState) -> None:
        """
        Reassign all internal basic state values and only
        trigger a notification afterwards.
        """
        assert len(args) == len(self)

        with self:
            for i, arg in enumerate(args):
                self[i].value = arg
