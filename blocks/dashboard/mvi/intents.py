"""Intents del bloque del panel principal."""

from __future__ import annotations

from dataclasses import dataclass

from core.mvi import Intent

from blocks.players.models import PlayerRecord
from blocks.telemetry.models import EventRecord


@dataclass(frozen=True)
class LoadDashboard(Intent):
    """Solicita consolidar el resumen del sistema."""

    event_limit: int = 8


@dataclass(frozen=True)
class RefreshDashboard(Intent):
    """Recargar el resumen (alias explicito de LoadDashboard)."""


@dataclass(frozen=True)
class DashboardLoaded(Intent):
    """Realimentacion: el resumen se consolido correctamente."""

    players: tuple[PlayerRecord, ...] = ()
    events: tuple[EventRecord, ...] = ()
    sessions_count: int = 0
    events_count: int = 0
    online: bool = False
    detail: str = ""
    degraded: tuple[str, ...] = ()


@dataclass(frozen=True)
class DashboardFailed(Intent):
    """Realimentacion: fallo total al consolidar el resumen."""

    message: str
