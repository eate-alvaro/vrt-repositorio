"""
Repositorio de eventos sobre el nodo `events` de Realtime Database.

Estructura:

    events/
      -NxAbc123/
        kind:       "disparo"
        detail:     "Disparo simulado. Municion restante: 29"
        actor:      "jugador01"
        severity:   "info"
        source:     "web"
        match_id:   "M-20260101-120000"
        created_at: "2026-01-01T12:00:00-04:00"

Las claves generadas por `POST` (push) ordenan cronologicamente, por lo que
`orderBy="$key"` con `limitToLast` devuelve los eventos mas recientes.
"""

from __future__ import annotations

from typing import Optional

from django.conf import settings

from core.services.firebase import get_client

from ..models import EventRecord


class EventRepository:
    """Acceso al nodo de eventos."""

    def __init__(self, client=None, node: str = "events") -> None:
        self._client = client or get_client()
        self._node = node

    def append(self, event: EventRecord) -> str:
        """Inserta un evento y devuelve la clave generada."""
        key = self._client.post(self._node, event.to_payload())
        return str(key or "")

    def recent(self, limit: int = 50) -> list[EventRecord]:
        """Ultimos `limit` eventos, del mas reciente al mas antiguo."""
        payload = self._client.get(
            self._node,
            params={"orderBy": '"$key"', "limitToLast": str(max(1, int(limit)))},
        )
        records = self._to_records(payload)
        records.reverse()
        return records

    def all(self) -> list[EventRecord]:
        records = self._to_records(self._client.get(self._node))
        records.reverse()
        return records

    def count(self) -> int:
        return len(self._client.keys(self._node))

    def clear(self) -> None:
        self._client.delete(self._node)

    def by_match(self, match_id: str) -> list[EventRecord]:
        records = [r for r in self.all() if r.match_id == match_id]
        return records

    # -- utilidades ---------------------------------------------------------
    @staticmethod
    def _to_records(payload: Optional[dict]) -> list[EventRecord]:
        if not isinstance(payload, dict):
            return []
        return [
            EventRecord.from_payload(key, value) for key, value in payload.items()
        ]
