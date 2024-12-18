"""
A basic state is a wrapper around a single value.
Either a generic object or a primitive.
"""

from __future__ import annotations

from typing import Any, Callable, Generic, Optional, TypeVar
from typing_extensions import Self

from .state import State
from .types import Serializable

T = TypeVar("T")
R = TypeVar("R")


class BasicState(State, Generic[T]):
    """
    A basic state contains a single value.

    Notifications are triggered on reassignment of the value.
    For primitive values, such as int and string, notifications are only triggered
    if the value changed on reassignment.
    """

    def __init__(self, value: T, verify_change: bool = True) -> None:
        """
        Initialize a basic state:

        Parameters
        ----------
        value: any
            the internal value of the state
        verify_change: bool, true per default
            verify if the value has changed on reassignment
        """
        super().__init__()

        self._verify_change = verify_change

        self.value = value

    def __setattr__(self, name: str, new_value: T) -> None:
        # ignore private attributes (begin with an underscore)
        if name[0] == "_":
            super().__setattr__(name, new_value)
            return

        # get the previous value for this attribute
        try:
            old_value = getattr(self, name)
        except AttributeError:
            # initial assignment
            super().__setattr__(name, new_value)
            return

        # verify if the attribute changed
        if self._verify_change and new_value == old_value:
            return

        # update the attribute
        super().__setattr__(name, new_value)

        # notify that the value changed
        self.notify_change()

    def set(self, value: T) -> None:
        """
        Simple function for the assignment of the value.

        This function is typically used in lambda functions where assignments are not possible.

        Parameters
        ----------
        value: any
            the new value
        """
        self.value = value

    def transform(
        self, self_to_other: Callable[[BasicState[T]], BasicState[R]]
    ) -> BasicState[R]:
        """
        Transform this state into another state.

        The new state is reactive to the changes of the old state.

        Parameters
        ----------
        self_to_other: Callable
            a function that transforms this state into a different state


        Returns
        -------
        BasicState
        """
        other_state = self_to_other(self)

        def _callback(_self: State) -> None:
            assert isinstance(_self, BasicState)
            other_state.set(self_to_other(_self).value)

        self.on_change(_callback)
        return other_state

    def __repr__(self) -> str:
        return f"{type(self).__name__}[value={self.value}]"

    def serialize(self) -> Serializable:
        raise NotImplementedError("Unable to serialize abstract basic state")

    def deserialize(self, _dict: Serializable) -> None:
        raise NotImplementedError("Unable to deserialize abstract basic state")

    def copy_from(self, other: Self) -> None:
        assert type(self) is type(
            other
        ), f"`copy_from` needs other[{type(other)=}] to be same type as self[{type(self)=}]"
        self.value = other.value


class IntState(BasicState[int]):
    """
    Implementation of the `BasicState` for an int.
    """

    def __init__(self, value: int) -> None:
        super().__init__(value, verify_change=True)

    def serialize(self) -> int:
        assert isinstance(self.value, int)
        return self.value


class FloatState(BasicState[float]):
    """
    Implementation of the `BasicState` for a float.

    Float states implement rounding of the number by specifying the desired precision.
    """

    def __init__(self, value: float, precision: Optional[int] = None) -> None:
        self._precision = precision

        super().__init__(value, verify_change=True)

    def __setattr__(self, name: str, new_value: float) -> None:
        if name == "value" and self._precision is not None:
            # apply precision if defined
            new_value = round(new_value, ndigits=self._precision)

        super().__setattr__(name, new_value)

    def serialize(self) -> float:
        assert isinstance(self.value, float)
        return self.value

    def round(self) -> IntState:
        return self.transform(lambda _: IntState(round(self.value)))


class StringState(BasicState[str]):
    """
    Implementation of the `BasicState` for a string.
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, verify_change=True)

    def serialize(self) -> str:
        assert isinstance(self.value, str)
        return self.value

    def __repr__(self) -> str:
        return f'{type(self).__name__}[value="{self.value}"]'


class BoolState(BasicState[bool]):
    """
    Implementation of the `BasicState` for a bool.
    """

    def __init__(self, value: bool) -> None:
        super().__init__(value, verify_change=True)

    def serialize(self) -> bool:
        assert isinstance(self.value, bool)
        return self.value


class ObjectState(BasicState[Any]):
    """
    Implementation of the `BasicState` for objects.

    This implementation does not verify changes of the internal value.
    Thus, the equals check to verify if the value changed is skipped.
    """

    def __init__(self, value: Any) -> None:
        super().__init__(value, verify_change=False)


# Mapping of primitive values types to their states.
BASIC_STATE_DICT = {
    str: StringState,
    int: IntState,
    float: FloatState,
    bool: BoolState,
}
