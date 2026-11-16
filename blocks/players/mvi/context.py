"""Contexto de ejecucion del bloque de jugadores."""

from __future__ import annotations

from dataclasses import dataclass

from django.http import HttpRequest

from blocks.telemetry.services.recorder import EventRecorder

from ..repositories.players import PlayerRepository


@dataclass(frozen=True)
class RosterContext:
    """Dependencias que necesitan los manejadores de efectos."""

    request: HttpRequest
    repository: PlayerRepository
    recorder: EventRecorder

    @property
    def actor_name(self) -> str:
        actor = getattr(self.request, "actor", None)
        return actor.username if actor else "anonimo"
