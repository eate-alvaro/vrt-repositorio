"""Reducer puro del bloque de historial."""

from __future__ import annotations

from typing import Sequence, Tuple

from core.mvi import Effect, Intent

from .effects import FetchEvents, PurgeEvents
from .intents import ClearHistory, HistoryFailed, HistoryLoaded, LoadHistory, SetSeverityFilter
from .state import FILTERS, HistoryState


def reduce_history(state: HistoryState, intent: Intent) -> Tuple[HistoryState, Sequence[Effect]]:
    if isinstance(intent, LoadHistory):
        return (
            state.evolve(status="loading", error="", limit=intent.limit),
            (FetchEvents(limit=intent.limit),),
        )

    if isinstance(intent, SetSeverityFilter):
        severity = intent.severity if intent.severity in FILTERS else "todos"
        return state.evolve(severity_filter=severity), ()

    if isinstance(intent, ClearHistory):
        return state.evolve(status="loading", error=""), (PurgeEvents(),)

    if isinstance(intent, HistoryLoaded):
        return (
            state.evolve(status="ready", events=tuple(intent.events), error=""),
            (),
        )

    if isinstance(intent, HistoryFailed):
        return state.evolve(status="failed", error=intent.message), ()

    return state, ()
