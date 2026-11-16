"""State: raiz del estado inmutable de cada bloque MVI."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


@dataclass(frozen=True)
class State:
    """Estado inmutable de un bloque.

    Se declara con `@dataclass(frozen=True)` para impedir mutaciones: el
    reducer siempre devuelve una instancia nueva.
    """

    def evolve(self, **changes: Any) -> "State":
        """Devuelve una copia con los campos indicados reemplazados."""
        return replace(self, **changes)
