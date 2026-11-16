"""Reducer puro del bloque del panel principal."""

from __future__ import annotations

from typing import Sequence, Tuple

from core.mvi import Effect, Intent

from .effects import FetchDashboardSnapshot
from .intents import DashboardFailed, DashboardLoaded, LoadDashboard, RefreshDashboard
from .state import DashboardState


def reduce_dashboard(state: DashboardState, intent: Intent) -> Tuple[DashboardState, Sequence[Effect]]:
    if isinstance(intent, LoadDashboard):
        return (
            state.evolve(status="loading", error=""),
            (FetchDashboardSnapshot(event_limit=intent.event_limit),),
        )

    if isinstance(intent, RefreshDashboard):
        return (
            state.evolve(status="loading", error=""),
            (FetchDashboardSnapshot(event_limit=8),),
        )

    if isinstance(intent, DashboardLoaded):
        return (
            state.evolve(
                status="ready",
                error="",
                players=tuple(intent.players),
                events=tuple(intent.events),
                sessions_count=intent.sessions_count,
                events_count=intent.events_count,
                online=intent.online,
                connection_detail=intent.detail,
                degraded=tuple(intent.degraded),
            ),
            (),
        )

    if isinstance(intent, DashboardFailed):
        return state.evolve(status="failed", error=intent.message), ()

    return state, ()
