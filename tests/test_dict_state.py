import pytest

from widget_state import IntState, DictState


class VectorState(DictState):
    def __init__(self, x: int, y: int, z: int):
        super().__init__()

        self.x = x
        self.y = y
        self.z = z


@pytest.fixture
def vector_state() -> VectorState:
    return VectorState(10, 20, 30)


def test_getitem(vector_state: VectorState) -> None:
    assert isinstance(vector_state[1], IntState)
    assert vector_state[1].value == 20


def test_len(vector_state: VectorState) -> None:
    assert len(vector_state) == 3


def test_values(vector_state: VectorState) -> None:
    assert vector_state.values() == [10, 20, 30]


def test_set(vector_state: VectorState) -> None:
    vector_state.set(1, 2, 3)
    assert isinstance(vector_state.x, IntState) and vector_state.x.value == 1
    assert isinstance(vector_state.y, IntState) and vector_state.y.value == 2
    assert isinstance(vector_state.z, IntState) and vector_state.z.value == 3
