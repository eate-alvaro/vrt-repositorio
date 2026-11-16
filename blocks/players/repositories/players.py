"""Repositorio del roster sobre el nodo `players` de Realtime Database."""

from __future__ import annotations

from dataclasses import replace
from typing import Optional

from django.utils import timezone

from core.services.firebase import get_client

from ..models import PlayerRecord


class PlayerRepository:
    """Acceso al nodo de jugadores."""

    def __init__(self, client=None, node: str = "players") -> None:
        self._client = client or get_client()
        self._node = node

    # -- lectura ------------------------------------------------------------
    def list_all(self) -> list[PlayerRecord]:
        payload = self._client.get(self._node)
        if not isinstance(payload, dict):
            return []
        records = [
            PlayerRecord.from_payload(key, value) for key, value in payload.items()
        ]
        return sorted(records, key=lambda r: (r.team, r.name.lower()))

    def count(self) -> int:
        return len(self._client.keys(self._node))

    def get(self, player_id: str) -> Optional[PlayerRecord]:
        payload = self._client.get(f"{self._node}/{player_id}")
        if not payload:
            return None
        return PlayerRecord.from_payload(player_id, payload)

    # -- escritura ----------------------------------------------------------
    def create(self, name: str, team: str = "azul") -> PlayerRecord:
        record = PlayerRecord(
            name=(name or "").strip(),
            team=team or "azul",
            status="activo",
            hits=0,
            shots=0,
            created_at=timezone.now().isoformat(timespec="seconds"),
        )
        key = self._client.post(self._node, record.to_payload())
        return replace(record, id=str(key or ""))

    def set_status(self, player_id: str, status: str) -> None:
        self._client.patch(f"{self._node}/{player_id}", {"status": status})

    def delete(self, player_id: str) -> None:
        self._client.delete(f"{self._node}/{player_id}")

    def bump_stats(self, player_id: str, *, shots: int = 0, hits: int = 0) -> None:
        """Incrementa disparos e impactos acumulados de un jugador."""
        record = self.get(player_id)
        if record is None:
            return
        self._client.patch(
            f"{self._node}/{player_id}",
            {"shots": record.shots + shots, "hits": record.hits + hits},
        )
