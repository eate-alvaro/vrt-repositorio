"""Estado inmutable del historial de eventos."""

from __future__ import annotations

from dataclasses import dataclass, field

from core.mvi import State

from blocks.telemetry.models import EventRecord

FILTERS = ("todos", "info", "success", "warning", "critical")


@dataclass(frozen=True)
class HistoryState(State):
    events: tuple[EventRecord, ...] = field(default_factory=tuple)
    severity_filter: str = "todos"
    status: str = "idle"  # idle | loading | ready | failed
    error: str = ""
    limit: int = 200

    @property
    def visible_events(self) -> tuple[EventRecord, ...]:
        if self.severity_filter == "todos":
            return self.events
        return tuple(e for e in self.events if e.severity == self.severity_filter)

    @property
    def total(self) -> int:
        return len(self.events)

    @property
    def shown(self) -> int:
        return len(self.visible_events)

    def count_by(self, severity: str) -> int:
        return sum(1 for e in self.events if e.severity == severity)
