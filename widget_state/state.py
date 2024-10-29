"""
Definition of the basic state class.
"""

from __future__ import annotations

from typing import Any, Callable, List, Optional, Union

from .types import Serializable


class State:
    """
    A state is a reactive wrapping around values.

    It contains a list of callbacks.
    Callbacks are registered with `on_change` and called when `notify_change` is triggered.
    Note that all attributes of a state that start with an underscore are private and changes are not tracked.
    Note that you can use `with <state>:` to change multiple values before notifying.
    """

    def __init__(self) -> None:
        self._callbacks: List[Callable[[State], None]] = []
        self._active = True
        self._enter_count = 0
        self._parent: Optional[State] = None

    def root(self) -> State:
        """
        Get the `root` state.

        This is the parent state without a parent.
        """
        if self._parent is None:
            return self
        return self._parent.root()

    def on_change(
        self, callback: Callable[[State], None], trigger: bool = False
    ) -> int:
        """
        Register a callback on this state.

        Parameters
        ----------
        callback: callable
            the callable to be registered
        trigger: bool
            if true, call the callback after registering

        Returns
        -------
        int
            an id of the callback which can be used to remove it
        """
        self._callbacks.append(callback)

        if trigger:
            callback(self)

        return len(self._callbacks) - 1

    def remove_callback(
        self, callback_or_id: Union[Callable[[State], None], int]
    ) -> None:
        """
        Remove a callback registered with `on_change`.

        Parameters
        ----------
        callback_or_id: callback or id
            either the callback or its id to be removed
        """
        if isinstance(callback_or_id, int):
            self._callbacks.pop(callback_or_id)
        else:
            self._callbacks.remove(callback_or_id)

    def notify_change(self) -> None:
        """
        Notify all callbacks that this state has changed.
        """
        if not self._active:
            return

        for cb in self._callbacks:
            cb(self)

    def __enter__(self) -> State:
        """
        Enter a state and deactivate notifications.
        """
        self._enter_count += 1
        self._active = False
        return self

    def __exit__(self, *_: Any) -> None:
        """
        Exit a state and trigger a notification.
        """
        self._enter_count = max(self._enter_count - 1, 0)
        if self._enter_count == 0:
            self._active = True
            self.notify_change()

    def serialize(self) -> Serializable:
        """
        Translate the state into a value that can be serialized as `json` or `yaml`.
        """
        raise NotImplementedError(
            "Serialize not implemented for abtract base class `State`"
        )

    def deserialize(self, _value: Serializable) -> None:
        """
        Resolve the state from a value deserialized by `json` or `yaml`.
        """
        raise NotImplementedError(
            "Deserialize not implemented for abtract base class `State`"
        )
