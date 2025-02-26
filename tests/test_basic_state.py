import pytest

from widget_state import (
    BasicState,
    NumberState,
    StringState,
    BoolState,
    ObjectState,
    ListState,
    Serializable,
)

from .util import MockCallback


@pytest.fixture
def callback() -> MockCallback:
    return MockCallback()


@pytest.fixture
def number_state(callback: MockCallback) -> NumberState:
    number_state = NumberState(0)
    number_state.on_change(callback)
    return number_state


def test_verify_change(number_state: NumberState, callback: MockCallback) -> None:
    _value = 5
    number_state.value = _value
    assert callback.n_calls == 1

    number_state.value = _value
    assert callback.n_calls == 1


def test_set(number_state: NumberState, callback: MockCallback) -> None:
    number_state.set(4)
    assert callback.n_calls == 1
    assert isinstance(callback.arg, NumberState)
    assert callback.arg.value == 4


@pytest.mark.parametrize(
    "state,expected",
    [
        (NumberState(2), "NumberState[value=2]"),
        (NumberState(3.141), "NumberState[value=3.141]"),
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
        (NumberState(2), 2),
        (NumberState(3.141), 3.141),
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
    res_state = NumberState(0.0)
    res_state.on_change(callback)

    list_state = ListState([NumberState(1), NumberState(2)])
    number_state = NumberState(3.5)

    def compute_sum() -> NumberState:
        _sum = sum(map(lambda _state: _state.value, [number_state, *list_state]))
        assert isinstance(_sum, float)
        return NumberState(_sum)

    res_state.depends_on(
        [list_state, number_state],
        compute_value=compute_sum,
        kwargs={list_state: {"element_wise": True}},
    )
    assert res_state.value == (1 + 2 + 3.5)

    number_state.value = 2.4
    assert res_state.value == (1 + 2 + 2.4)

    list_state[0].value = 3
    assert res_state.value == (3 + 2 + 2.4)


def test_transform(number_state: NumberState, callback: MockCallback) -> None:
    transformed_state = number_state.transform(
        lambda state: NumberState(state.value**2)
    )
    assert transformed_state.value == 0

    number_state.value = 3
    assert transformed_state.value == 9


def test_number_state_precision() -> None:
    number_state = NumberState(3.141, precision=2)

    assert number_state.value == 3.14

    number_state.value = 2.745
    assert number_state.value == 2.75
