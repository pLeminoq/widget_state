from __future__ import annotations

from typing import Union

Primitive = Union[int, float, str, bool]
Serializable = Union[Primitive, list["Serializable"], dict[str, "Serializable"]]
