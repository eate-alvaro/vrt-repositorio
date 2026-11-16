"""Fabrica del Store MVI del bloque de jugadores."""

from __future__ import annotations

from core.mvi import Store, create_store

from .context import RosterContext
from .handlers import create_handlers
from .reducer import reduce_roster
from .state import RosterState


def create_roster_store(
    context: RosterContext, state: RosterState | None = None
) -> Store[RosterState]:
    return create_store(state or RosterState(), reduce_roster, create_handlers(context))
