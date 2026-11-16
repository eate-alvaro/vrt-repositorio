"""
Identidad del usuario autenticado.

El actor es el resultado del bloque `accounts`: un valor inmutable que viaja
por la sesion de Django y que el resto de bloques consume sin conocer Firebase.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Actor:
    """Usuario autenticado dentro de la plataforma."""

    username: str
    display_name: str = ""
    role: str = "operator"

    @property
    def initials(self) -> str:
        source = (self.display_name or self.username or "?").strip()
        parts = [p for p in source.replace(".", " ").replace("_", " ").split() if p]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[1][0]).upper()

    @property
    def label(self) -> str:
        return self.display_name or self.username

    def to_session(self) -> dict[str, str]:
        return {
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role,
        }

    @classmethod
    def from_session(cls, payload: dict) -> "Actor | None":
        if not isinstance(payload, dict) or not payload.get("username"):
            return None
        return cls(
            username=str(payload.get("username", "")),
            display_name=str(payload.get("display_name", "")),
            role=str(payload.get("role", "operator")),
        )
