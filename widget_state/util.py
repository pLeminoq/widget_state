"""
Decorator to create computed states.

A computed state is the result of applying a function to other states.
If one of these states changes, the compute state is computed anew.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, ParamSpec, TypeVar

from .basic_state import BasicState
from .state import State

T = TypeVar("T", bound=BasicState[Any])
P = ParamSpec("P")

S = TypeVar("S", bound=State)


def computed_state(
    func: Callable[P, T],
) -> Callable[P, T]:
    """
    Computed annotation for states.

    A computed state is computed from one or more other states.
    It is defined by a computation function.
    A computed state can either be defined by a separate function or as a function and
    state of a higher state.

    Example:
    class SquareNumber(HigherState):

        def __init__(self, number: int):
            super().__init__()

            self.number = number
            self.squared = self.squared(self.number)

        @computed
        def squared(self, number: IntState) -> IntState:
            return IntState(number.value * number.value)

    """

    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        # compute initial value
        computed_value = func(*args, **kwargs)

        # create function that updates the computed value
        def _on_change(_: Any) -> None:
            computed_value.value = func(*args, **kwargs).value

        # handling of computed states as values of higher states
        _args = args[1:] if func.__code__.co_varnames[0] == "self" else args

        # register callback on depending state
        for _arg in _args:
            assert isinstance(
                _arg, State
            ), f"Variable {_arg} of computed state {func.__name__} is not a basic state"
            _arg.on_change(_on_change)

        # return computed value
        return computed_value

    return wrapped


def compute(
    states: Iterable[State],
    compute_value: Callable[[], S],
    kwargs: dict[State, dict[str, Any]] = {},
) -> S:
    res = compute_value()

    for state in states:
        _kwargs = {} if state not in kwargs else kwargs[state]
        state.on_change(lambda _: res.copy_from(compute_value()), **_kwargs)

    return res
