"""
Definition of a HigherOrderState.
This is a state with other states as values.
"""

import pytest

from widget_state import (
    FloatState,
    IntState,
    StringState,
    ObjectState,
    HigherOrderState,
    computed,
)

from .util import MockCallback


@pytest.fixture
def callback() -> MockCallback:
    return MockCallback()


class NestedState(HigherOrderState):
    def __init__(self) -> None:
        super().__init__()
        self.length = FloatState(3.141)


class SuperState(HigherOrderState):
    def __init__(self) -> None:
        super().__init__()
        self.name = StringState("Higher")
        self.count = IntState(5)
        self.nested = NestedState()


@pytest.fixture
def super_state() -> SuperState:
    return SuperState()


def test_set_attr(super_state: SuperState, callback: MockCallback) -> None:
    super_state.on_change(callback)

    assert super_state.name.value == "Higher"
    assert super_state.count.value == 5
    assert super_state.nested.length.value == 3.141

    super_state.name.value = "Even higher"
    super_state.count.value = 7
    super_state.nested.length.value = 2.714
    assert callback.n_calls == 3


def test_dict(super_state: SuperState) -> None:
    _dict = super_state.dict()
    assert _dict == {
        "name": super_state.name,
        "count": super_state.count,
        "nested": super_state.nested,
    }


def test_serialize(super_state: SuperState) -> None:
    serialized = super_state.serialize()
    assert serialized == {"name": "Higher", "count": 5, "nested": {"length": 3.141}}


def test_serialize_with_unserializable(super_state: SuperState) -> None:
    super_state.obj = ObjectState(123)

    serialized = super_state.serialize()
    # states which are not serializable should be ignored on serialization
    assert serialized == {"name": "Higher", "count": 5, "nested": {"length": 3.141}}


def test_deserialize(super_state: SuperState, callback: MockCallback) -> None:
    super_state.on_change(callback)
    super_state.deserialize({"name": "Test", "count": 7, "nested": {"length": 2.714}})

    assert super_state.name.value == "Test"
    assert super_state.count.value == 7
    assert super_state.nested.length.value == 2.714
    assert callback.n_calls == 1


_str = """\
[SuperState]:
 - name: StringState[value="Higher"]
 - count: IntState[value=5]
 - nested[NestedState]:
  - length: FloatState[value=3.141]\
"""


def test_to_str(super_state: SuperState) -> None:
    assert super_state.to_str() == _str
    assert str(super_state) == _str


def test_copy_from(super_state: SuperState) -> None:
    new_state = SuperState()
    new_state.name.value = "Test"
    new_state.count.value = 2
    new_state.nested.length.value = 2.71

    super_state.copy_from(new_state)
    assert super_state.name.value == "Test"
    assert super_state.count.value == 2
    assert super_state.nested.length.value == 2.71


def test_computed() -> None:
    class ExampleState(HigherOrderState):
        def __init__(self):
            super().__init__()

            self.a = IntState(0)
            self.b = IntState(1)

            self._validate_computed_states()

        @computed
        def sum(self, a: IntState, b: IntState) -> IntState:
            return IntState(a.value + b.value)

    ex = ExampleState()
    assert ex.sum.value == 1
    ex.a.value = 5
    assert ex.sum.value == 6
