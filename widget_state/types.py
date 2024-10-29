"""
Types used by the widget_state library.
"""

from __future__ import annotations

Primitive = int | float | str | bool
Serializable = Primitive | list["Serializable"] | dict[str, "Serializable"]
