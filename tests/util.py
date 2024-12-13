from typing import Optional

from widget_state import State


class MockCallback:
    def __init__(self) -> None:
        self.n_calls = 0
        self.arg: Optional[State] = None

    def __call__(self, state: State) -> None:
        self.n_calls += 1
        self.arg = state
