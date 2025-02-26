"""
A basic state is a wrapper around a single value.
Either a generic object or a primitive.
"""

from __future__ import annotations

from typing import Any, Callable, Generic, Optional, TypeVar
from typing_extensions import Self

from .state import State
from .types import Serializable
from .util import compute

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
        self,
        self_to_other: Callable[[BasicState[T]], BasicState[R]],
        other_to_self: Callable[[BasicState[R]], BasicState[T]] = None,
    ) -> BasicState[R]:
        """
        Transform this state into another state.

        The new state is reactive to the changes of the old state.

        Parameters
        ----------
        self_to_other: Callable
            a function that transforms this state into a different state
        other_to_self: Callable
            a function that transforms this state back to self
            note that the mapping must be bidirectional, since otherwise updating
            one value creates an infinite notification loop.

        Returns
        -------
        BasicState
        """
        other = self_to_other(self)

        self.on_change(lambda _: other.set(self_to_other(self).value))
        if other_to_self is not None:
            other.on_change(lambda _: self.set(other_to_self(other).value))

        return other

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


NT = TypeVar("NT", int, float)


class NumberState(BasicState[NT]):
    def __init__(self, value: NT, precision: Optional[int] = None) -> None:
        self._precision = precision

        super().__init__(value, verify_change=True)

    def __add__(self, other: NumberState[NT]):
        return compute([self, other], lambda: NumberState(self.value + other.value))

    def __sub__(self, other: NumberState[NT]):
        return compute([self, other], lambda: NumberState(self.value - other.value))

    def __mul__(self, other: NumberState[NT]):
        return compute([self, other], lambda: NumberState(self.value * other.value))

    def __truediv__(self, other: NumberState[NT]):
        return compute([self, other], lambda: NumberState(self.value / other.value))

    def __mod__(self, other: NumberState[NT]):
        return compute([self, other], lambda: NumberState(self.value % other.value))

    def __floordiv__(self, other: NumberState[NT]):
        return compute([self, other], lambda: NumberState(self.value // other.value))

    def __pow__(self, other: NumberState[NT]):
        return compute([self, other], lambda: NumberState(self.value**other.value))

    def __neg__(self):
        return compute([self], lambda: NumberState(-self.value))

    def serialize(self) -> NT:
        return self.value

    def round(self) -> NumberState[int]:
        return self.transform(lambda _: IntState(round(self.value)))

    def str(self, format_str: str = "{}") -> StringState:
        return self.transform(lambda _: StringState(format_str.format(self.value)))

    def __setattr__(self, name: str, new_value: NT) -> None:
        if name == "value" and self._precision is not None:
            # apply precision if defined
            new_value = round(new_value, ndigits=self._precision)

        super().__setattr__(name, new_value)


class IntState(NumberState[int]):
    """
    Implementation of the `BasicState` for an int.
    """

    def __init__(self, value: int) -> None:
        super().__init__(value)

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
    int: NumberState,
    float: NumberState,
    bool: BoolState,
}
