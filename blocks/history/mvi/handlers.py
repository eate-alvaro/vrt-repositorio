"""Manejadores de efectos del bloque de historial."""

from __future__ import annotations

import logging
from functools import partial
from typing import Dict, Iterable, Type, Union

from core.mvi import Effect, Intent, Store
from core.services.firebase import FirebaseError

from blocks.telemetry.repositories.events import EventRepository

from .effects import FetchEvents, PurgeEvents
from .intents import HistoryFailed, HistoryLoaded, LoadHistory

logger = logging.getLogger("vrt.history")

Feedback = Union[None, Intent, Iterable[Intent]]


class HistoryContext:
    """Dependencias de los manejadores del historial."""

    def __init__(self, repository: EventRepository | None = None) -> None:
        self.repository = repository or EventRepository()


def create_handlers(context: HistoryContext) -> Dict[Type[Effect], object]:
    return {
        FetchEvents: partial(_fetch_events, context),
        PurgeEvents: partial(_purge_events, context),
    }


def _fetch_events(context: HistoryContext, store: Store, effect: FetchEvents) -> Feedback:
    try:
        events = context.repository.recent(effect.limit)
    except FirebaseError as exc:
        logger.warning("No se pudo leer la telemetria: %s", exc)
        return HistoryFailed(
            message="No se pudo leer el nodo `events` en Firebase Realtime Database."
        )
    return HistoryLoaded(events=tuple(events))


def _purge_events(context: HistoryContext, store: Store, effect: PurgeEvents) -> Feedback:
    try:
        context.repository.clear()
    except FirebaseError as exc:
        logger.warning("No se pudo vaciar la telemetria: %s", exc)
        return HistoryFailed(message="No se pudo vaciar el nodo `events` en Firebase.")
    return LoadHistory()
