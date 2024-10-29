import pytest

from widget_state import (
    BasicState,
    IntState,
    StringState,
    BoolState,
    FloatState,
    ObjectState,
    ListState,
    Serializable,
)

from .util import MockCallback


@pytest.fixture
def callback() -> MockCallback:
    return MockCallback()


@pytest.fixture
def int_state(callback: MockCallback) -> IntState:
    int_state = IntState(0)
    int_state.on_change(callback)
    return int_state


def test_verify_change(int_state: IntState, callback: MockCallback) -> None:
    _value = 5
    int_state.value = _value
    assert callback.n_calls == 1

    int_state.value = _value
    assert callback.n_calls == 1


def test_set(int_state: IntState, callback: MockCallback) -> None:
    int_state.set(4)
    assert callback.n_calls == 1
    assert isinstance(callback.arg, IntState)
    assert callback.arg.value == 4


@pytest.mark.parametrize(
    "state,expected",
    [
        (IntState(2), "IntState[value=2]"),
        (FloatState(3.141), "FloatState[value=3.141]"),
        (StringState("Hello World"), 'StringState[value="Hello World"]'),
        (BoolState(False), "BoolState[value=False]"),
        (ObjectState([]), "ObjectState[value=[]]"),
    ],
)
def test_repr(state: BasicState, expected: str) -> None:
    assert state.__repr__() == expected


@pytest.mark.parametrize(
    "state,expected",
    [
        (IntState(2), 2),
        (FloatState(3.141), 3.141),
        (StringState("Hello World"), "Hello World"),
        (BoolState(False), False),
    ],
)
def test_serialize(state: BasicState, expected: Serializable) -> None:
    assert state.serialize() == expected


def test_serialize_with_object_state() -> None:
    obj_state = ObjectState([])
    with pytest.raises(NotImplementedError):
        obj_state.serialize()


def test_depends_on(callback: MockCallback) -> None:
    res_state = FloatState(0.0)
    res_state.on_change(callback)

    list_state = ListState([IntState(1), IntState(2)])
    float_state = FloatState(3.5)

    def compute_sum() -> float:
        _sum = sum(map(lambda _state: _state.value, [float_state, *list_state]))
        assert isinstance(_sum, float)
        return _sum

    res_state.depends_on(
        [list_state, float_state],
        compute_value=compute_sum,
        element_wise=True,
    )
    assert res_state.value == (1 + 2 + 3.5)

    float_state.value = 2.4
    assert res_state.value == (1 + 2 + 2.4)

    assert isinstance(list_state[0], IntState)  # check for typing
    list_state[0].value = 3
    assert res_state.value == (3 + 2 + 2.4)

    list_state.append(FloatState(1.2))
    assert res_state.value == (3 + 2 + +1.2 + 2.4)


def test_transform(int_state: IntState, callback: MockCallback) -> None:
    transformed_state = int_state.transform(lambda state: IntState(state.value**2))
    assert transformed_state.value == 0

    int_state.value = 3
    assert transformed_state.value == 9


def test_float_state_precision() -> None:
    float_state = FloatState(3.141, precision=2)

    assert float_state.value == 3.14

    float_state.value = 2.745
    assert float_state.value == 2.75
