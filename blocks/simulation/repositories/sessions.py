"""Repositorio del nodo `sessions` (espejo de las partidas)."""

from __future__ import annotations

from typing import Any

from django.utils import timezone

from core.services.firebase import get_client


class SessionRepository:
    """Escribe el espejo de cada partida en Realtime Database."""

    def __init__(self, client=None, node: str = "sessions") -> None:
        self._client = client or get_client()
        self._node = node

    def save(self, match_id: str, payload: dict[str, Any]) -> None:
        data = dict(payload)
        data["updated_at"] = timezone.now().isoformat(timespec="seconds")
        self._client.put(f"{self._node}/{match_id}", data)

    def get(self, match_id: str) -> dict | None:
        return self._client.get(f"{self._node}/{match_id}")

    def count(self) -> int:
        return len(self._client.keys(self._node))
