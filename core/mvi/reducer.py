"""Reducer: funcion pura `(State, Intent) -> (State, efectos)`."""

from __future__ import annotations

from typing import Callable, Sequence, Tuple, TypeVar

from .effect import Effect
from .intent import Intent
from .state import State

StateT = TypeVar("StateT", bound=State)

# Contrato del reducer: estado nuevo + efectos a ejecutar.
Reducer = Callable[[StateT, Intent], Tuple[StateT, Sequence[Effect]]]

# Resultado sin cambios ni efectos.
NO_EFFECTS: tuple[Effect, ...] = ()


def no_change(state: StateT) -> Tuple[StateT, Sequence[Effect]]:
    """Reducer neutro: devuelve el estado tal cual, sin efectos."""
    return state, NO_EFFECTS
