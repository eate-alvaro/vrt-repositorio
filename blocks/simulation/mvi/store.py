"""Fabrica del Store MVI del bloque de simulacion."""

from __future__ import annotations

from core.mvi import Store, create_store

from .context import MatchContext
from .handlers import create_handlers
from .reducer import reduce_match
from .state import MatchState


def create_match_store(
    context: MatchContext, state: MatchState | None = None
) -> Store[MatchState]:
    return create_store(state or MatchState(), reduce_match, create_handlers(context))
