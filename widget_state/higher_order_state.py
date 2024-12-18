"""
Definition of a HigherOrderState - a state that groups other states.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Union, ParamSpec, TypeVar
from typing_extensions import Self

from .basic_state import BASIC_STATE_DICT, BasicState, ObjectState
from .state import State
from .types import Serializable

T = TypeVar("T", bound=State)
P = ParamSpec("P")


def computed(func: Callable[P, T]) -> Callable[P, T]:
    """
    Mark a function of a `HigherOrderState` as computed.

    This means that the value computed by this function will be added to
    the state as an attribute. It is available once all parameters have
    been set as attributes to the state.

    Example:
    class ExampleState(HigherOrderState):

        def __init__(self):
            super().__init__()

            self.a = IntState(0)
            self.b = IntState(1)

        @computed
        def sum(self, a: IntState, b: IntState) -> IntState:
            return IntState(a.value + b.value)

    ex = ExampleState()
    assert ex.sum.value == 1
    ex.a.value = 5
    assert ex.sum.value == 6
    """
    setattr(func, "is_computed_state", True)
    setattr(
        func,
        "params",
        list(
            filter(
                lambda name: name != "self", inspect.signature(func).parameters.keys()
            )
        ),
    )
    return func


class HigherOrderState(State):
    """
    A higher order state is a collection of other states.

    A higher order state automatically notifies a change if one of its internal states change.
    If a value (not a state) is added to a higher state, it will automatically be wrapped into
    a state type.
    """

    def __init__(self):
        super().__init__()

        self._computed_states = dict(
            filter(
                lambda member: inspect.ismethod(member[1])
                and hasattr(member[1], "is_computed_state"),
                inspect.getmembers(self),
            )
        )
        # self._access_count = dict([(name, 0) for name in self._computed_states.keys()])
        # print(f"{self.__class__.__name__}: {self._access_count=}, {self._computed_states.keys()=}")

    def _update_computed_state(self, name: str) -> None:
        func = self._computed_states[name]
        params = list(map(lambda param_name: getattr(self, param_name), func.params))
        self.__dict__[name].copy_from(func(*params))

    def __setattr__(self, name: str, value: Union[Any, State]) -> None:
        # ignore private attributes (begin with an underscore)
        if name[0] == "_":
            super().__setattr__(name, value)
            return

        # wrap non-state values into states
        if not isinstance(value, State):
            value = BASIC_STATE_DICT.get(type(value), ObjectState)(value)

        # assert that states are not reassigned as only their values should change
        assert not hasattr(self, name) or callable(
            getattr(self, name)
        ), f"Reassignment of value {name} in state {self}"
        # assert that all attributes are states
        assert isinstance(
            value, State
        ), f"Values of higher states must be states not {type(value)}"

        # update the attribute
        super().__setattr__(name, value)

        # set self as parent of added state to build a state hierarchy
        value._parent = self

        # register notification to the internal state
        value.on_change(lambda _: self.notify_change())

        # update computed states
        for computed_state_name, func in self._computed_states.items():
            # skip computed states that are already initialized
            if computed_state_name in self.__dict__:
                continue

            # skip computed states whose params are not yet available
            if not all(map(lambda param_name: hasattr(self, param_name), func.params)):
                continue

            params = list(
                map(lambda param_name: getattr(self, param_name), func.params)
            )

            # skip if a param is not a state
            # this can happen if a computed states depends on another computed state
            if not all(map(lambda param: isinstance(param, State), params)):
                continue

            # re-compute every time a parameter changes
            for param in params:
                param.on_change(
                    lambda _, _name=computed_state_name: self._update_computed_state(
                        _name
                    )
                )

            # initialize computed state
            self.__setattr__(computed_state_name, func(*params))

    def __getattribute__(self, name) -> Any:
        attr = super().__getattribute__(name)

        if inspect.ismethod(attr) and hasattr(attr, "is_computed_state"):
            """
            TODO:
              * activate when a debug flag is set?
              * is is possible to make this check only after the init method of the subclass?
            """
            # print(f"Warning: access to not yet initialized computed state: {name}!")

        # print(f"HO get attr {name=}, {type(attr)=}")
        return attr

    def dict(self) -> dict[str, State]:
        """
        Create a dictionary mapping names to states of all internal states.

        Returns
        -------
        Dict[str, State]
        """
        labels = list(
            filter(lambda label: not label.startswith("_"), self.__dict__.keys())
        )
        return {label: getattr(self, label) for label in labels}

    def serialize(self) -> Serializable:
        res = {}
        for key, value in self.dict().items():
            try:
                res[key] = value.serialize()
            except NotImplementedError:
                pass
        return res

    def deserialize(self, _dict: Serializable) -> None:
        assert isinstance(
            _dict, dict
        ), "HigherState can only be serialized from dict[str, Serializable]"
        with self:
            for key, value in _dict.items():
                attr = getattr(self, key)

                if issubclass(type(attr), BasicState):
                    attr._active = False
                    attr.value = value
                    attr._active = True
                    continue

                attr.deserialize(value)

    def __str__(self) -> str:
        return self.to_str()

    def to_str(self, padding: int = 0) -> str:
        """
        Create a string representation of this HigherOrderState.

        The padding parameter is used to recursively print internal
        HigherOrderStates.

        Parameters
        ----------
        padding: int
            padding applied to each line in the resulting string
        """
        _strs = []
        for key, value in self.dict().items():
            if isinstance(value, HigherOrderState):
                _strs.append(f"{key}{value.to_str(padding=padding+1)}")
            else:
                _strs.append(f"{key}: {value}")

        _padding = " " * padding
        return f"[{type(self).__name__}]:\n{_padding} - " + f"\n{_padding} - ".join(
            _strs
        )

    def copy_from(self, other: Self) -> None:
        assert type(self) is type(
            other
        ), f"`copy_from` needs other[type(other)] to be same type as self[{type(self)}]"

        with self:
            dict_self = self.dict()
            dict_other = other.dict()

            for key, value in dict_self.items():
                value.copy_from(dict_other[key])
