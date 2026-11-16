"""Intents del bloque de historial."""

from __future__ import annotations

from dataclasses import dataclass

from core.mvi import Intent

from blocks.telemetry.models import EventRecord


@dataclass(frozen=True)
class LoadHistory(Intent):
    """Solicita leer la telemetria desde el nodo `events`."""

    limit: int = 200


@dataclass(frozen=True)
class SetSeverityFilter(Intent):
    """Cambiar el filtro de severidad (operacion puramente local)."""

    severity: str = "todos"


@dataclass(frozen=True)
class ClearHistory(Intent):
    """Vaciar el nodo `events`."""


@dataclass(frozen=True)
class HistoryLoaded(Intent):
    """Realimentacion: la telemetria se leyo correctamente."""

    events: tuple[EventRecord, ...]


@dataclass(frozen=True)
class HistoryFailed(Intent):
    """Realimentacion: no se pudo leer o vaciar la telemetria."""

    message: str
