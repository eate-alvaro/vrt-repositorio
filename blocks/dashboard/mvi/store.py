"""Fabrica del Store MVI del bloque del panel principal."""

from __future__ import annotations

from core.mvi import Store, create_store

from .handlers import DashboardContext, create_handlers
from .reducer import reduce_dashboard
from .state import DashboardState


def create_dashboard_store(
    context: DashboardContext, state: DashboardState | None = None
) -> Store[DashboardState]:
    return create_store(state or DashboardState(), reduce_dashboard, create_handlers(context))
