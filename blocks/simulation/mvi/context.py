"""Contexto de ejecucion del bloque de simulacion."""

from __future__ import annotations

from dataclasses import dataclass

from django.http import HttpRequest

from blocks.telemetry.services.recorder import EventRecorder

from ..repositories.sessions import SessionRepository


@dataclass(frozen=True)
class MatchContext:
    request: HttpRequest
    sessions: SessionRepository
    recorder: EventRecorder

    @property
    def actor_name(self) -> str:
        actor = getattr(self.request, "actor", None)
        return actor.username if actor else "anonimo"
