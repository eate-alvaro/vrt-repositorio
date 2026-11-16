"""Modelo de dominio del roster de jugadores."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

TEAMS = ("azul", "rojo", "verde", "amarillo")
STATUSES = ("activo", "inactivo")


@dataclass(frozen=True)
class PlayerRecord:
    """Participante registrado en el nodo `players`."""

    id: str = ""
    name: str = ""
    team: str = "azul"
    status: str = "activo"
    hits: int = 0
    shots: int = 0
    created_at: str = ""

    @property
    def is_active(self) -> bool:
        return self.status == "activo"

    @property
    def initials(self) -> str:
        parts = [p for p in (self.name or "?").split() if p]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[1][0]).upper()

    def to_payload(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "team": self.team,
            "status": self.status,
            "hits": self.hits,
            "shots": self.shots,
            "created_at": self.created_at,
        }

    @classmethod
    def from_payload(cls, key: str, payload: dict | None) -> "PlayerRecord":
        payload = payload or {}
        return cls(
            id=str(key),
            name=str(payload.get("name", "")),
            team=str(payload.get("team", "azul")),
            status=str(payload.get("status", "activo")),
            hits=int(payload.get("hits", 0) or 0),
            shots=int(payload.get("shots", 0) or 0),
            created_at=str(payload.get("created_at", "")),
        )
