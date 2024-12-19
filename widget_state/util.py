"""
Decorator to create computed states.

A computed state is the result of applying a function to other states.
If one of these states changes, the compute state is computed anew.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, TypeVar

from .state import State

S = TypeVar("S", bound=State)


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
