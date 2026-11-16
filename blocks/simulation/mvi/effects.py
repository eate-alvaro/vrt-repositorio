"""Efectos declarativos del bloque de simulacion."""

from __future__ import annotations

from dataclasses import dataclass

from core.mvi import Effect

from .state import MatchState


@dataclass(frozen=True)
class PersistMatch(Effect):
    """Guardar el estado de la partida (sesion + nodo `sessions`)."""

    snapshot: MatchState


@dataclass(frozen=True)
class RecordMatchEvent(Effect):
    """Emitir un evento de telemetria de la partida."""

    kind: str
    detail: str
    severity: str = "info"
    match_id: str = ""
