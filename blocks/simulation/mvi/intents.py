"""Intents del bloque de simulacion."""

from __future__ import annotations

from dataclasses import dataclass

from core.mvi import Intent


@dataclass(frozen=True)
class StartMatch(Intent):
    """Iniciar una partida nueva.

    El identificador y el instante se inyectan desde la vista para mantener el
    reducer libre de dependencias del reloj.
    """

    match_id: str
    started_at: str


@dataclass(frozen=True)
class Shoot(Intent):
    """Registrar un disparo."""


@dataclass(frozen=True)
class RegisterHit(Intent):
    """Registrar un impacto recibido."""

    received_at: str = ""


@dataclass(frozen=True)
class FinishMatch(Intent):
    """Finalizar la partida en curso."""

    finished_at: str = ""


@dataclass(frozen=True)
class ResetMatch(Intent):
    """Restablecer los indicadores de la partida."""
