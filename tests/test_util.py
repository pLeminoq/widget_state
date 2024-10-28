import pytest

from widget_state import FloatState, HigherOrderState, computed_state

from .util import MockCallback


class Sum(HigherOrderState):

    def __init__(self):
        super().__init__()

        self.a = 0.5
        self.b = 2.0
        self.sum = self.sum(self.a, self.b)

    @computed_state
    def sum(self, a, b):
        return FloatState(a.value + b.value)


def test_computed_state():
    callback = MockCallback()
    _sum = Sum()
    _sum.on_change(callback)

    assert _sum.sum.value == 2.5

    _sum.a.value = 1.0
    assert _sum.sum.value == 3.0
    assert callback.n_calls == 2  # first a changes and then sum

    _sum.b.value = -2.0
    assert _sum.sum.value == -1.0
    assert callback.n_calls == 4  # first b changes and then sum
