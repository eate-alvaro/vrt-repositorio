"""Manejadores de efectos del bloque de jugadores."""

from __future__ import annotations

import logging
from functools import partial
from typing import Dict, Iterable, Type, Union

from core.mvi import Effect, Intent, Store
from core.services.firebase import FirebaseError

from .context import RosterContext
from .effects import DeletePlayer, FetchPlayers, LogRosterEvent, PersistPlayer, UpdatePlayerStatus
from .intents import LoadRoster, RosterFailed

logger = logging.getLogger("vrt.players")

Feedback = Union[None, Intent, Iterable[Intent]]


def create_handlers(context: RosterContext) -> Dict[Type[Effect], object]:
    return {
        FetchPlayers: partial(_fetch_players, context),
        PersistPlayer: partial(_persist_player, context),
        DeletePlayer: partial(_delete_player, context),
        UpdatePlayerStatus: partial(_update_status, context),
        LogRosterEvent: partial(_log_event, context),
    }


def _fetch_players(context: RosterContext, store: Store, effect: FetchPlayers) -> Feedback:
    try:
        players = context.repository.list_all()
    except FirebaseError as exc:
        logger.warning("No se pudo leer el roster: %s", exc)
        return RosterFailed(
            message="No se pudo leer el nodo `players` en Firebase Realtime Database."
        )
    from .intents import RosterLoaded

    return RosterLoaded(players=tuple(players))


def _persist_player(context: RosterContext, store: Store, effect: PersistPlayer) -> Feedback:
    try:
        context.repository.create(effect.name, effect.team)
    except FirebaseError as exc:
        logger.warning("No se pudo crear el jugador: %s", exc)
        return RosterFailed(
            message="No se pudo escribir en el nodo `players`. Revisa las reglas de Firebase."
        )
    return LoadRoster()


def _delete_player(context: RosterContext, store: Store, effect: DeletePlayer) -> Feedback:
    try:
        context.repository.delete(effect.player_id)
    except FirebaseError as exc:
        logger.warning("No se pudo eliminar el jugador: %s", exc)
        return RosterFailed(message="No se pudo eliminar el jugador en Firebase.")
    return LoadRoster()


def _update_status(context: RosterContext, store: Store, effect: UpdatePlayerStatus) -> Feedback:
    try:
        context.repository.set_status(effect.player_id, effect.status)
    except FirebaseError as exc:
        logger.warning("No se pudo actualizar el jugador: %s", exc)
        return RosterFailed(message="No se pudo actualizar el estado del jugador.")
    return LoadRoster()


def _log_event(context: RosterContext, store: Store, effect: LogRosterEvent) -> Feedback:
    context.recorder.record(
        effect.kind,
        effect.detail,
        actor=context.actor_name,
        severity=effect.severity,
        source="web",
    )
    return None
