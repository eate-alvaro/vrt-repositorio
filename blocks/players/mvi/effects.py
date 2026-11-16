"""Efectos declarativos del bloque de jugadores."""

from __future__ import annotations

from dataclasses import dataclass

from core.mvi import Effect


@dataclass(frozen=True)
class FetchPlayers(Effect):
    """Leer el nodo `players`."""


@dataclass(frozen=True)
class PersistPlayer(Effect):
    """Insertar un jugador en el nodo `players`."""

    name: str
    team: str


@dataclass(frozen=True)
class DeletePlayer(Effect):
    """Eliminar un jugador del nodo `players`."""

    player_id: str


@dataclass(frozen=True)
class UpdatePlayerStatus(Effect):
    """Cambiar el estado de un jugador."""

    player_id: str
    status: str


@dataclass(frozen=True)
class LogRosterEvent(Effect):
    """Emitir un evento de telemetria asociado al roster."""

    kind: str
    detail: str
    severity: str = "info"
