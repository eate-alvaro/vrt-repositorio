"""
Servicio de consolidacion del panel principal.

Lee los nodos `players`, `events` y `sessions` y arma una fotografia unica.
Cada lectura es tolerante a fallos: si un nodo no responde, el resto del panel
sigue siendo util.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from core.services.firebase import FirebaseError, get_client
from blocks.players.models import PlayerRecord
from blocks.players.repositories.players import PlayerRepository
from blocks.simulation.repositories.sessions import SessionRepository
from blocks.telemetry.models import EventRecord
from blocks.telemetry.repositories.events import EventRepository

logger = logging.getLogger("vrt.dashboard")


@dataclass(frozen=True)
class DashboardSnapshot:
    players: tuple[PlayerRecord, ...] = field(default_factory=tuple)
    events: tuple[EventRecord, ...] = field(default_factory=tuple)
    sessions_count: int = 0
    events_count: int = 0
    online: bool = False
    detail: str = ""
    degraded: tuple[str, ...] = field(default_factory=tuple)

    # -- metricas derivadas -------------------------------------------------
    @property
    def players_total(self) -> int:
        return len(self.players)

    @property
    def players_active(self) -> int:
        return sum(1 for p in self.players if p.is_active)

    @property
    def total_shots(self) -> int:
        return sum(p.shots for p in self.players)

    @property
    def total_hits(self) -> int:
        return sum(p.hits for p in self.players)

    @property
    def accuracy(self) -> int:
        return int(round(self.total_hits / self.total_shots * 100)) if self.total_shots else 0

    @property
    def critical_events(self) -> int:
        return sum(1 for e in self.events if e.severity == "critical")

    @property
    def warning_events(self) -> int:
        return sum(1 for e in self.events if e.severity == "warning")


class DashboardService:
    """Consolida el estado del sistema para el panel principal."""

    def __init__(
        self,
        players: PlayerRepository | None = None,
        events: EventRepository | None = None,
        sessions: SessionRepository | None = None,
    ) -> None:
        self._players = players or PlayerRepository()
        self._events = events or EventRepository()
        self._sessions = sessions or SessionRepository()

    def snapshot(self, *, event_limit: int = 8) -> DashboardSnapshot:
        degraded: list[str] = []

        players: tuple[PlayerRecord, ...] = ()
        try:
            players = tuple(self._players.list_all())
        except FirebaseError as exc:
            logger.warning("Panel: fallo al leer players: %s", exc)
            degraded.append("players")

        events: tuple[EventRecord, ...] = ()
        try:
            events = tuple(self._events.recent(event_limit))
        except FirebaseError as exc:
            logger.warning("Panel: fallo al leer events: %s", exc)
            degraded.append("events")

        sessions_count = 0
        try:
            sessions_count = self._sessions.count()
        except FirebaseError as exc:
            logger.warning("Panel: fallo al leer sessions: %s", exc)
            degraded.append("sessions")

        events_count = 0
        try:
            events_count = self._events.count()
        except FirebaseError as exc:
            degraded.append("events:count")

        online, detail = get_client().health()

        return DashboardSnapshot(
            players=players,
            events=events,
            sessions_count=sessions_count,
            events_count=events_count,
            online=online,
            detail=detail,
            degraded=tuple(sorted(set(degraded))),
        )
