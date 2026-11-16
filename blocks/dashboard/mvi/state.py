"""Estado inmutable del panel principal."""

from __future__ import annotations

from dataclasses import dataclass, field

from core.mvi import State

from blocks.players.models import PlayerRecord
from blocks.telemetry.models import EventRecord


@dataclass(frozen=True)
class DashboardState(State):
    status: str = "idle"  # idle | loading | ready | failed
    error: str = ""
    players: tuple[PlayerRecord, ...] = field(default_factory=tuple)
    events: tuple[EventRecord, ...] = field(default_factory=tuple)
    sessions_count: int = 0
    events_count: int = 0
    online: bool = False
    connection_detail: str = ""
    degraded: tuple[str, ...] = field(default_factory=tuple)

    # -- derivados ----------------------------------------------------------
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
    def connection_label(self) -> str:
        if self.status == "loading":
            return "consultando"
        return "en linea" if self.online else "sin conexion"

    @property
    def has_degraded(self) -> bool:
        return bool(self.degraded)
