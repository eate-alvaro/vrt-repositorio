"""
Registrador de eventos.

Centraliza la escritura de telemetria para que cualquier bloque (simulacion,
jugadores, cuentas) emita eventos homogeneos sin conocer los detalles de
Realtime Database.
"""

from __future__ import annotations

import logging
from dataclasses import replace

from django.utils import timezone

from core.services.firebase import FirebaseError

from ..models import EventRecord
from ..repositories.events import EventRepository

logger = logging.getLogger("vrt.telemetry")


class EventRecorder:
    """Escribe eventos en el nodo `events` (mejor esfuerzo)."""

    def __init__(self, repository: EventRepository | None = None) -> None:
        self._repository = repository or EventRepository()

    def record(
        self,
        kind: str,
        detail: str = "",
        *,
        actor: str = "",
        severity: str = "info",
        source: str = "web",
        match_id: str = "",
    ) -> EventRecord:
        event = EventRecord(
            kind=kind,
            detail=detail,
            actor=actor,
            severity=severity,
            source=source,
            match_id=match_id,
            created_at=timezone.now().isoformat(timespec="seconds"),
        )
        try:
            key = self._repository.append(event)
        except FirebaseError as exc:
            logger.warning("No se pudo registrar el evento '%s': %s", kind, exc)
            return event
        return replace(event, id=key)

    def recent(self, limit: int = 50) -> list[EventRecord]:
        return self._repository.recent(limit)

    def count(self) -> int:
        return self._repository.count()


def record_event(kind: str, detail: str = "", **kwargs) -> EventRecord:
    """Atajo funcional para registrar un evento puntual."""
    return EventRecorder().record(kind, detail, **kwargs)
