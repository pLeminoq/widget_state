"""
Module containing the definition of the `DictState`.
A higher order state that contains only basic states as child states.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from .basic_state import BasicState
from .higher_order_state import HigherOrderState
from .types import Primitive


class DictState(HigherOrderState):
    """
    A dict state is a utility state - a higher state that only contains basic states.

    It enables iteration, access by index and other utility functions.
    """

    def __init__(self) -> None:
        """
        Initialize a dict state.
        """
        super().__init__()
        self._labels: list[str] = []

    def __setattr__(self, name: str, new_value: Any | BasicState[Any]) -> None:
        super().__setattr__(name, new_value)

        if name[0] == "_":
            return

        if name not in self._labels:
            self._labels.append(name)

    def __getitem__(self, i: int) -> BasicState[Any]:
        item = self.__getattribute__(self._labels[i])
        assert isinstance(item, BasicState)
        return item

    def __iter__(self) -> Iterator[BasicState[Any]]:
        return iter(map(self.__getattribute__, self._labels))

    def __len__(self) -> int:
        return len(self._labels)

    def values(self) -> list[Any]:
        """
        Get the values of all internal states as a list.
        """
        return [attr.value for attr in self]

    def set(
        self,
        *args: BasicState[Any] | Primitive,
        **kwargs: BasicState[Any] | Primitive,
    ) -> None:
        """
        Reassign internal basic state values and only
        trigger a notification afterwards.
        """
        assert len(args) <= len(self)

        with self:
            for i, arg in enumerate(args):
                self[i].value = arg.value if isinstance(arg, BasicState) else arg

            _dict = self.dict()
            for name, kwarg in kwargs.items():
                attr = _dict[name]
                assert isinstance(attr, BasicState)
                attr.value = kwarg.value if isinstance(kwarg, BasicState) else kwarg
