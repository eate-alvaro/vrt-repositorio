"""
Modelo de dominio de la telemetria.

Un `EventRecord` representa un evento capturado por la plataforma: un disparo,
un impacto, el inicio de una partida o una lectura de un sensor IoT (ESP32).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SEVERITIES = ("info", "success", "warning", "critical")
SOURCES = ("web", "godot", "esp32", "mqtt", "sistema")


@dataclass(frozen=True)
class EventRecord:
    """Evento de telemetria almacenado en el nodo `events`."""

    id: str = ""
    kind: str = ""
    detail: str = ""
    actor: str = ""
    severity: str = "info"
    source: str = "web"
    match_id: str = ""
    created_at: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "detail": self.detail,
            "actor": self.actor,
            "severity": self.severity,
            "source": self.source,
            "match_id": self.match_id,
            "created_at": self.created_at,
        }

    @classmethod
    def from_payload(cls, key: str, payload: dict | None) -> "EventRecord":
        payload = payload or {}
        return cls(
            id=str(key),
            kind=str(payload.get("kind", "")),
            detail=str(payload.get("detail", "")),
            actor=str(payload.get("actor", "")),
            severity=str(payload.get("severity", "info")),
            source=str(payload.get("source", "web")),
            match_id=str(payload.get("match_id", "")),
            created_at=str(payload.get("created_at", "")),
        )

    @property
    def time_label(self) -> str:
        """Hora legible (HH:MM:SS) a partir del instante ISO almacenado."""
        raw = self.created_at
        if not raw:
            return "--:--:--"
        try:
            from django.utils.dateparse import parse_datetime
            from django.utils import timezone

            parsed = parse_datetime(raw)
            if parsed is None:
                return raw[11:19] if len(raw) >= 19 else raw
            if timezone.is_naive(parsed):
                parsed = timezone.make_aware(parsed)
            return timezone.localtime(parsed).strftime("%H:%M:%S")
        except (ValueError, TypeError):
            return raw[11:19] if len(raw) >= 19 else raw
