import pytest

from widget_state import IntState, ListState

from .util import MockCallback


@pytest.fixture
def callback() -> MockCallback:
    return MockCallback()


@pytest.fixture
def list_state() -> ListState:
    list_state = ListState(
        [
            IntState(1),
            IntState(2),
            IntState(3),
        ]
    )
    return list_state


@pytest.fixture
def observed_list_state(list_state: ListState, callback: MockCallback) -> ListState:
    list_state.on_change(callback)
    return list_state


@pytest.fixture
def element_wise_observed_list_state(
    list_state: ListState, callback: MockCallback
) -> ListState:
    list_state.on_change(callback, element_wise=True)
    return list_state


def test_on_change_with_element_wise(
    list_state: ListState, callback: MockCallback
) -> None:
    list_state.on_change(callback, element_wise=True)

    elem_state = list_state[0]
    assert isinstance(elem_state, IntState)
    elem_state.value = 10
    assert callback.n_calls == 1


def test_remove_callback_by_id(list_state: ListState, callback: MockCallback) -> None:
    _id = list_state.on_change(callback)
    list_state.remove_callback(_id)
    assert callback not in list_state._callbacks


def test_remove_callback_with_element_wise(
    list_state: ListState, callback: MockCallback
) -> None:
    list_state.on_change(callback, element_wise=True)
    list_state.remove_callback(callback)

    elem_state = list_state[0]
    assert isinstance(elem_state, IntState)
    elem_state.value = 10
    assert callback.n_calls == 0


def test_append(observed_list_state: ListState, callback: MockCallback) -> None:
    new_state = IntState(4)
    observed_list_state.append(new_state)

    assert observed_list_state[-1] == new_state
    assert callback.n_calls == 1
    assert new_state.root() == observed_list_state

    new_state.value = 10
    assert callback.n_calls == 1


def test_append_with_element_wise(
    element_wise_observed_list_state: ListState, callback: MockCallback
) -> None:
    new_state = IntState(4)
    element_wise_observed_list_state.append(new_state)
    new_state.value = 10

    assert callback.n_calls == 2


def test_insert(observed_list_state: ListState, callback: MockCallback) -> None:
    new_state = IntState(-1)
    observed_list_state.insert(1, new_state)

    assert observed_list_state[1] == new_state
    assert callback.n_calls == 1
    assert new_state.root() == observed_list_state
    assert observed_list_state._elem_obs in new_state._callbacks


def test_extend(observed_list_state: ListState, callback: MockCallback) -> None:
    observed_list_state.extend([IntState(4), IntState(5)])

    assert len(observed_list_state) == 5
    assert callback.n_calls == 1


def test_pop(observed_list_state: ListState, callback: MockCallback) -> None:
    _state = observed_list_state.pop()

    assert len(observed_list_state) == 2
    assert _state not in observed_list_state
    assert _state._parent is None
    assert observed_list_state._elem_obs not in _state._callbacks


def test_remove(observed_list_state: ListState, callback: MockCallback) -> None:
    _state = observed_list_state[0]
    observed_list_state.remove(_state)

    assert len(observed_list_state) == 2
    assert _state not in observed_list_state
    assert _state._parent is None
    assert observed_list_state._elem_obs not in _state._callbacks


def test_clear(observed_list_state: ListState, callback: MockCallback) -> None:
    _state = observed_list_state[0]
    observed_list_state.clear()

    assert len(observed_list_state) == 0
    assert callback.n_calls == 1
    assert _state._parent is None
    assert observed_list_state._elem_obs not in _state._callbacks


def test_index(list_state: ListState) -> None:
    _state = list_state[1]
    assert list_state.index(_state) == 1


def test_reverse(observed_list_state: ListState, callback: MockCallback) -> None:
    _0, _1, _2 = observed_list_state
    observed_list_state.reverse()

    assert observed_list_state._list == [_2, _1, _0]
    assert callback.n_calls == 1


def test_sort(observed_list_state: ListState, callback: MockCallback) -> None:
    _state = IntState(-1)
    observed_list_state.append(_state)
    observed_list_state.sort(
        key=lambda int_state: int_state.value if isinstance(int_state, IntState) else 0
    )

    assert observed_list_state[0] == _state
    assert callback.n_calls == 2


def test_serialize(list_state: ListState) -> None:
    assert list_state.serialize() == [1, 2, 3]


def test_deserialize(list_state: ListState) -> None:
    with pytest.raises(NotImplementedError):
        list_state.deserialize([0, 1, 2])


def test_copy_from(list_state: ListState) -> None:
    new_list: ListState[IntState] = ListState()
    new_list.copy_from(list_state)

    assert len(new_list) == len(list_state)
    for i in range(len(new_list)):
        assert new_list[i].value == list_state[i].value
