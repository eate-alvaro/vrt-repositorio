"""Reducer puro del bloque de jugadores."""

from __future__ import annotations

from typing import Sequence, Tuple

from core.mvi import Effect, Intent

from .effects import DeletePlayer, FetchPlayers, LogRosterEvent, PersistPlayer, UpdatePlayerStatus
from .intents import (
    AddPlayer,
    LoadRoster,
    RemovePlayer,
    RosterFailed,
    RosterLoaded,
    TogglePlayer,
)
from .state import RosterState


def reduce_roster(state: RosterState, intent: Intent) -> Tuple[RosterState, Sequence[Effect]]:
    if isinstance(intent, LoadRoster):
        return state.evolve(status="loading", error=""), (FetchPlayers(),)

    if isinstance(intent, AddPlayer):
        name = (intent.name or "").strip()
        if not name:
            return (
                state.evolve(status="failed", error="El nombre del jugador es obligatorio."),
                (),
            )
        if any(p.name.lower() == name.lower() for p in state.players):
            return (
                state.evolve(status="failed", error=f"'{name}' ya esta en el roster."),
                (),
            )
        return (
            state.evolve(status="loading", error="", notice="", form_name=name, form_team=intent.team),
            (
                PersistPlayer(name=name, team=intent.team),
                LogRosterEvent(kind="roster:alta", detail=f"Jugador '{name}' agregado al equipo {intent.team}."),
            ),
        )

    if isinstance(intent, RemovePlayer):
        target = next((p for p in state.players if p.id == intent.player_id), None)
        detail = f"Jugador '{target.name}' eliminado del roster." if target else "Jugador eliminado del roster."
        return (
            state.evolve(status="loading", error="", notice=""),
            (
                DeletePlayer(player_id=intent.player_id),
                LogRosterEvent(kind="roster:baja", detail=detail, severity="warning"),
            ),
        )

    if isinstance(intent, TogglePlayer):
        target = next((p for p in state.players if p.id == intent.player_id), None)
        if target is None:
            return state.evolve(status="failed", error="Jugador no encontrado."), ()
        new_status = "inactivo" if target.is_active else "activo"
        severity = "info" if new_status == "activo" else "warning"
        return (
            state.evolve(status="loading", error="", notice=""),
            (
                UpdatePlayerStatus(player_id=target.id, status=new_status),
                LogRosterEvent(
                    kind="roster:estado",
                    detail=f"Jugador '{target.name}' -> {new_status}.",
                    severity=severity,
                ),
            ),
        )

    if isinstance(intent, RosterLoaded):
        return (
            state.evolve(
                status="ready",
                players=tuple(intent.players),
                error="",
                notice="",
                form_name="",
                form_team="azul",
            ),
            (),
        )

    if isinstance(intent, RosterFailed):
        return state.evolve(status="failed", error=intent.message), ()

    return state, ()
