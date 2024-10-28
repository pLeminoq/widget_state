import pytest

from widget_state import FloatState, IntState, StringState, ObjectState, HigherOrderState

from .util import MockCallback


@pytest.fixture
def callback() -> MockCallback:
    return MockCallback()


@pytest.fixture
def higher_order_state() -> HigherOrderState:
    state = HigherOrderState()
    state.name = "Higher"
    state.count = 5
    state.internal = HigherOrderState()
    state.internal.length = 3.141
    return state


def test_set_attr(higher_order_state, callback):
    higher_order_state.on_change(callback)

    assert isinstance(higher_order_state.name, StringState)
    assert higher_order_state.name.value == "Higher"

    assert isinstance(higher_order_state.count, IntState)
    assert higher_order_state.count.value == 5

    assert isinstance(higher_order_state.internal.length, FloatState)
    assert higher_order_state.internal.length.value == 3.141

    higher_order_state.name.value = "Even higher"
    higher_order_state.count.value = 7
    higher_order_state.internal.length.value = 2.714
    assert callback.n_calls == 3


def test_dict(higher_order_state):
    _dict = higher_order_state.dict()
    assert _dict == {
        "name": higher_order_state.name,
        "count": higher_order_state.count,
        "internal": higher_order_state.internal,
    }


def test_serialize(higher_order_state):
    serialized = higher_order_state.serialize()
    assert serialized == {"name": "Higher", "count": 5, "internal": {"length": 3.141}}


def test_serialize_with_unserializable(higher_order_state):
    higher_order_state.obj = ObjectState(123)

    serialized = higher_order_state.serialize()
    # states which are not serializable should be ignored on serialization
    assert serialized == {"name": "Higher", "count": 5, "internal": {"length": 3.141}}


def test_deserialize(higher_order_state, callback):
    higher_order_state.on_change(callback)
    higher_order_state.deserialize(
        {"name": "Test", "count": 7, "internal": {"length": 2.714}}
    )

    assert higher_order_state.name.value == "Test"
    assert higher_order_state.count.value == 7
    assert higher_order_state.internal.length.value == 2.714
    assert callback.n_calls == 1


_str ="""\
[HigherOrderState]:
 - name: StringState[value="Higher"]
 - count: IntState[value=5]
 - internal[HigherOrderState]:
  - length: FloatState[value=3.141]\
"""
def test_to_str(higher_order_state):
    assert higher_order_state.to_str() == _str
    assert str(higher_order_state) == _str
