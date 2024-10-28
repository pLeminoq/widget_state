from __future__ import annotations

from typing import Any, Union, Protocol

Primitive = Union[int, float, str, bool]
Serializable = Union[Primitive, list["Serializable"], dict[str, "Serializable"]]

class SupportsLT(Protocol):

    def __lt__(self, other: Any) -> bool: ...
