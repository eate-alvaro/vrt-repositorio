"""Efectos declarativos del bloque del panel principal."""

from __future__ import annotations

from dataclasses import dataclass

from core.mvi import Effect


@dataclass(frozen=True)
class FetchDashboardSnapshot(Effect):
    """Leer players + events + sessions y verificar la conexion."""

    event_limit: int = 8
