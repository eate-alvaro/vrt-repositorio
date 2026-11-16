"""Manejadores de efectos del bloque de simulacion."""

from __future__ import annotations

import logging
from functools import partial
from typing import Dict, Iterable, Type, Union

from core.mvi import Effect, Intent, Store
from core.services.firebase import FirebaseError

from ..services.session import save_match
from .context import MatchContext
from .effects import PersistMatch, RecordMatchEvent

logger = logging.getLogger("vrt.simulation")

Feedback = Union[None, Intent, Iterable[Intent]]


def create_handlers(context: MatchContext) -> Dict[Type[Effect], object]:
    return {
        PersistMatch: partial(_persist_match, context),
        RecordMatchEvent: partial(_record_event, context),
    }


def _persist_match(context: MatchContext, store: Store, effect: PersistMatch) -> Feedback:
    snapshot = effect.snapshot
    # 1) Estado autoritativo de la sesion del navegador.
    save_match(context.request, snapshot)
    # 2) Espejo en el nodo `sessions` de Realtime Database (mejor esfuerzo).
    if snapshot.match_id:
        try:
            context.sessions.save(
                snapshot.match_id,
                snapshot.to_payload(actor=context.actor_name),
            )
        except FirebaseError as exc:
            logger.warning("No se pudo sincronizar la partida con Firebase: %s", exc)
    return None


def _record_event(context: MatchContext, store: Store, effect: RecordMatchEvent) -> Feedback:
    context.recorder.record(
        effect.kind,
        effect.detail,
        actor=context.actor_name,
        severity=effect.severity,
        source="web",
        match_id=effect.match_id,
    )
    return None
