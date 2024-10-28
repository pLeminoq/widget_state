import pytest

from widget_state import IntState, DictState


@pytest.fixture
def dict_state() -> DictState:
    return DictState({"x": 10, "y": 20, "z": 30})

def test_getitem(dict_state):
    assert isinstance(dict_state[1], IntState)
    assert dict_state[1].value == 20

def test_iter(dict_state):
    pass

def test_len(dict_state):
    assert len(dict_state) == 3

def test_values(dict_state):
    assert dict_state.values() == [10, 20, 30]

def test_set(dict_state):
    dict_state.set(1, 2, 3)
    assert dict_state.x.value == 1
    assert dict_state.y.value == 2
    assert dict_state.z.value == 3
