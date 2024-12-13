import pytest

from widget_state import State

from .util import MockCallback


@pytest.fixture
def state() -> State:
    return State()


@pytest.fixture
def callback() -> MockCallback:
    return MockCallback()


def test_root(state: State) -> None:
    assert state.root() == state


def test_on_change(state: State, callback: MockCallback) -> None:
    state.on_change(callback)

    assert callback in state._callbacks
    assert callback.n_calls == 0


def test_on_change_with_trigger(state: State, callback: MockCallback) -> None:
    state.on_change(callback, trigger=True)

    assert callback in state._callbacks
    assert callback.n_calls == 1


def test_remove_callback(state: State, callback: MockCallback) -> None:
    state.on_change(callback)
    state.remove_callback(callback)

    assert callback not in state._callbacks


def test_remove_callback_with_id(state: State, callback: MockCallback) -> None:
    callback_id = state.on_change(callback)
    state.remove_callback(callback_id)

    assert callback not in state._callbacks


def test_notify_change(state: State, callback: MockCallback) -> None:
    state.on_change(callback)
    state.notify_change()

    assert callback.n_calls == 1
    assert callback.arg == state


def test_enter_and_exit_state(state: State, callback: MockCallback) -> None:
    state.on_change(callback)
    with state:
        state.notify_change()
        assert callback.n_calls == 0

        with state:
            pass

        assert callback.n_calls == 0
    assert callback.n_calls == 1


def test_serialize(state: State) -> None:
    with pytest.raises(NotImplementedError):
        state.serialize()


def test_deserialize(state: State) -> None:
    with pytest.raises(NotImplementedError):
        state.deserialize(0)


def test_copy_from(state: State) -> None:
    with pytest.raises(NotImplementedError):
        state.copy_from(state)
