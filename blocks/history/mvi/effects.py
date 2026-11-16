"""Efectos declarativos del bloque de historial."""

from __future__ import annotations

from dataclasses import dataclass

from core.mvi import Effect


@dataclass(frozen=True)
class FetchEvents(Effect):
    """Leer los ultimos eventos del nodo `events`."""

    limit: int = 200


@dataclass(frozen=True)
class PurgeEvents(Effect):
    """Eliminar todo el contenido del nodo `events`."""
