from widget_state import FloatState, compute


def test_compute() -> None:
    a = FloatState(0.5)
    b = FloatState(2.0)
    sum = compute([a, b], lambda: FloatState(a.value + b.value))

    assert sum.value == 2.5

    a.value = 1.0
    assert sum.value == 3.0

    b.value = -2.0
    assert sum.value == -1.0
