"""Estado inmutable de la partida de simulacion."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.mvi import State

MAX_HP = 100
MAX_AMMO = 30
HIT_DAMAGE = 20


@dataclass(frozen=True)
class MatchState(State):
    """Estado completo de la partida actual."""

    active: bool = False
    hp: int = MAX_HP
    max_hp: int = MAX_HP
    ammo: int = MAX_AMMO
    max_ammo: int = MAX_AMMO
    score: int = 0
    shots: int = 0
    hits: int = 0
    match_id: str = ""
    started_at: str = ""
    finished_at: str = ""
    last_kind: str = ""
    last_detail: str = ""
    last_severity: str = "info"

    # -- derivados ----------------------------------------------------------
    @property
    def hp_percent(self) -> int:
        return int(round(self.hp / self.max_hp * 100)) if self.max_hp else 0

    @property
    def ammo_percent(self) -> int:
        return int(round(self.ammo / self.max_ammo * 100)) if self.max_ammo else 0

    @property
    def accuracy(self) -> int:
        return int(round(self.hits / self.shots * 100)) if self.shots else 0

    @property
    def hp_state(self) -> str:
        if self.hp_percent <= 25:
            return "danger"
        if self.hp_percent <= 55:
            return "warning"
        return "ok"

    @property
    def phase(self) -> str:
        if self.active:
            return "en curso"
        if self.finished_at:
            return "finalizada"
        return "en espera"

    @property
    def has_feedback(self) -> bool:
        return bool(self.last_detail)

    # -- serializacion ------------------------------------------------------
    def to_session(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "ammo": self.ammo,
            "max_ammo": self.max_ammo,
            "score": self.score,
            "shots": self.shots,
            "hits": self.hits,
            "match_id": self.match_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "last_kind": self.last_kind,
            "last_detail": self.last_detail,
            "last_severity": self.last_severity,
        }

    def to_payload(self, *, actor: str = "", updated_at: str = "") -> dict[str, Any]:
        payload = self.to_session()
        payload["actor"] = actor
        payload["updated_at"] = updated_at
        return payload

    @classmethod
    def from_session(cls, payload: dict | None) -> "MatchState":
        if not isinstance(payload, dict):
            return cls()
        try:
            return cls(
                active=bool(payload.get("active", False)),
                hp=int(payload.get("hp", MAX_HP)),
                max_hp=int(payload.get("max_hp", MAX_HP)),
                ammo=int(payload.get("ammo", MAX_AMMO)),
                max_ammo=int(payload.get("max_ammo", MAX_AMMO)),
                score=int(payload.get("score", 0)),
                shots=int(payload.get("shots", 0)),
                hits=int(payload.get("hits", 0)),
                match_id=str(payload.get("match_id", "")),
                started_at=str(payload.get("started_at", "")),
                finished_at=str(payload.get("finished_at", "")),
                last_kind=str(payload.get("last_kind", "")),
                last_detail=str(payload.get("last_detail", "")),
                last_severity=str(payload.get("last_severity", "info")),
            )
        except (TypeError, ValueError):
            return cls()
