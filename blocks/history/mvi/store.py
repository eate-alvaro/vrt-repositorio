"""Fabrica del Store MVI del bloque de historial."""

from __future__ import annotations

from core.mvi import Store, create_store

from .handlers import HistoryContext, create_handlers
from .reducer import reduce_history
from .state import HistoryState


def create_history_store(
    context: HistoryContext, state: HistoryState | None = None
) -> Store[HistoryState]:
    return create_store(state or HistoryState(), reduce_history, create_handlers(context))
