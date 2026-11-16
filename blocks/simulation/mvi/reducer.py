"""Reducer puro del bloque de simulacion.

Toda la logica de la partida vive aqui y es determinista: dados el estado y el
intent, el resultado siempre es el mismo. La persistencia se declara como
efecto, nunca se ejecuta.
"""

from __future__ import annotations

from typing import Sequence, Tuple

from core.mvi import Effect, Intent

from .effects import PersistMatch, RecordMatchEvent
from .intents import FinishMatch, RegisterHit, ResetMatch, Shoot, StartMatch
from .state import HIT_DAMAGE, MAX_AMMO, MAX_HP, MatchState


def _feedback(state: MatchState, kind: str, detail: str, severity: str = "warning") -> MatchState:
    """Estado con un aviso para la interfaz (no genera telemetria)."""
    return state.evolve(last_kind=kind, last_detail=detail, last_severity=severity)


def reduce_match(state: MatchState, intent: Intent) -> Tuple[MatchState, Sequence[Effect]]:
    # -- iniciar -----------------------------------------------------------
    if isinstance(intent, StartMatch):
        fresh = MatchState(
            active=True,
            hp=MAX_HP,
            ammo=MAX_AMMO,
            score=0,
            shots=0,
            hits=0,
            match_id=intent.match_id,
            started_at=intent.started_at,
            last_kind="partida:inicio",
            last_detail=f"Partida {intent.match_id} iniciada.",
            last_severity="success",
        )
        return fresh, (
            PersistMatch(snapshot=fresh),
            RecordMatchEvent(
                kind="partida:inicio",
                detail=f"Partida {intent.match_id} iniciada.",
                severity="success",
                match_id=intent.match_id,
            ),
        )

    # -- disparo -----------------------------------------------------------
    if isinstance(intent, Shoot):
        if not state.active:
            return _feedback(state, "aviso", "Primero inicia la partida."), ()
        if state.ammo <= 0:
            return _feedback(state, "aviso", "No queda municion en el marcador."), ()
        updated = state.evolve(
            ammo=state.ammo - 1,
            shots=state.shots + 1,
            score=state.score + 10,
            last_kind="disparo",
            last_detail=f"Disparo detectado. Municion restante: {state.ammo - 1}.",
            last_severity="info",
        )
        return updated, (
            PersistMatch(snapshot=updated),
            RecordMatchEvent(
                kind="disparo",
                detail=updated.last_detail,
                severity="info",
                match_id=state.match_id,
            ),
        )

    # -- impacto -----------------------------------------------------------
    if isinstance(intent, RegisterHit):
        if not state.active:
            return _feedback(state, "aviso", "Primero inicia la partida."), ()
        hp = max(0, state.hp - HIT_DAMAGE)
        eliminated = hp <= 0
        updated = state.evolve(
            hp=hp,
            hits=state.hits + 1,
            active=not eliminated,
            finished_at=intent.received_at if eliminated else state.finished_at,
            last_kind="jugador:eliminado" if eliminated else "impacto",
            last_detail=(
                "Jugador eliminado: la vida llego a cero."
                if eliminated
                else f"Impacto recibido. Vida restante: {hp}."
            ),
            last_severity="critical" if eliminated else "warning",
        )
        return updated, (
            PersistMatch(snapshot=updated),
            RecordMatchEvent(
                kind=updated.last_kind,
                detail=updated.last_detail,
                severity=updated.last_severity,
                match_id=state.match_id,
            ),
        )

    # -- finalizar ---------------------------------------------------------
    if isinstance(intent, FinishMatch):
        if not state.active:
            return _feedback(state, "aviso", "No hay una partida activa."), ()
        updated = state.evolve(
            active=False,
            finished_at=intent.finished_at,
            last_kind="partida:fin",
            last_detail=f"Partida finalizada. Puntuacion: {state.score}.",
            last_severity="success",
        )
        return updated, (
            PersistMatch(snapshot=updated),
            RecordMatchEvent(
                kind="partida:fin",
                detail=updated.last_detail,
                severity="success",
                match_id=state.match_id,
            ),
        )

    # -- reiniciar ---------------------------------------------------------
    if isinstance(intent, ResetMatch):
        fresh = MatchState(
            last_kind="partida:reset",
            last_detail="Indicadores restablecidos.",
            last_severity="info",
        )
        return fresh, (
            PersistMatch(snapshot=fresh),
            RecordMatchEvent(
                kind="partida:reset",
                detail="Indicadores de partida restablecidos.",
                severity="info",
                match_id="",
            ),
        )

    return state, ()
