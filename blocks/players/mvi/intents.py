"""Intents del bloque de jugadores."""

from __future__ import annotations

from dataclasses import dataclass

from core.mvi import Intent

from ..models import PlayerRecord


@dataclass(frozen=True)
class LoadRoster(Intent):
    """Solicita leer el roster desde Realtime Database."""


@dataclass(frozen=True)
class AddPlayer(Intent):
    """Registrar un jugador nuevo."""

    name: str
    team: str = "azul"


@dataclass(frozen=True)
class RemovePlayer(Intent):
    """Eliminar un jugador del roster."""

    player_id: str


@dataclass(frozen=True)
class TogglePlayer(Intent):
    """Alternar el estado activo/inactivo de un jugador."""

    player_id: str


@dataclass(frozen=True)
class RosterLoaded(Intent):
    """Realimentacion: el roster se leyo correctamente."""

    players: tuple[PlayerRecord, ...]


@dataclass(frozen=True)
class RosterFailed(Intent):
    """Realimentacion: no se pudo operar contra el backend."""

    message: str
