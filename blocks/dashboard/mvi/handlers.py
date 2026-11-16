"""Manejadores de efectos del bloque del panel principal."""

from __future__ import annotations

import logging
from functools import partial
from typing import Dict, Iterable, Type, Union

from core.mvi import Effect, Intent, Store

from ..services.snapshot import DashboardService
from .effects import FetchDashboardSnapshot
from .intents import DashboardLoaded, DashboardFailed

logger = logging.getLogger("vrt.dashboard")

Feedback = Union[None, Intent, Iterable[Intent]]


class DashboardContext:
    """Dependencias de los manejadores del panel."""

    def __init__(self, service: DashboardService | None = None) -> None:
        self.service = service or DashboardService()


def create_handlers(context: DashboardContext) -> Dict[Type[Effect], object]:
    return {FetchDashboardSnapshot: partial(_fetch_snapshot, context)}


def _fetch_snapshot(
    context: DashboardContext, store: Store, effect: FetchDashboardSnapshot
) -> Feedback:
    try:
        snapshot = context.service.snapshot(event_limit=effect.event_limit)
    except Exception as exc:  # defensivo: el panel nunca debe romper la pagina
        logger.exception("Fallo inesperado al consolidar el panel: %s", exc)
        return DashboardFailed(message="No se pudo consolidar el resumen del sistema.")

    return DashboardLoaded(
        players=snapshot.players,
        events=snapshot.events,
        sessions_count=snapshot.sessions_count,
        events_count=snapshot.events_count,
        online=snapshot.online,
        detail=snapshot.detail,
        degraded=snapshot.degraded,
    )
