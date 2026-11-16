"""Estado inmutable del roster."""

from __future__ import annotations

from dataclasses import dataclass, field

from core.mvi import State

from ..models import PlayerRecord


@dataclass(frozen=True)
class RosterState(State):
    players: tuple[PlayerRecord, ...] = field(default_factory=tuple)
    status: str = "idle"  # idle | loading | ready | failed
    error: str = ""
    notice: str = ""
    form_name: str = ""
    form_team: str = "azul"

    @property
    def total(self) -> int:
        return len(self.players)

    @property
    def active_count(self) -> int:
        return sum(1 for p in self.players if p.is_active)

    @property
    def inactive_count(self) -> int:
        return self.total - self.active_count

    @property
    def is_failed(self) -> bool:
        return self.status == "failed"
