from __future__ import annotations

from typing import Any, Callable

from .basic_state import BasicState


def computed_state(
    func: Callable[[BasicState], BasicState]
) -> Callable[[BasicState], BasicState]:
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
    # save function name and argument names
    name = func.__name__
    varnames = func.__code__.co_varnames[1:]

    def wrapped(*args: BasicState) -> BasicState:
        # compute initial value
        computed_value = func(*args)

        # create function that updates the computed value
        def _on_change(_: Any) -> None:
            computed_value.value = func(*args).value

        # handling of computed states as values of higher states
        _args = args[1:] if func.__code__.co_varnames[0] == "self" else args

        # validate arguments are states
        for _arg in _args:
            assert isinstance(
                _arg, BasicState
            ), f"Variable {_arg} of computed state {func.__name__} is not a basic state"

        # register callback on depending state
        for _arg in _args:
            _arg.on_change(_on_change)

        # return computed value
        return computed_value

    return wrapped
