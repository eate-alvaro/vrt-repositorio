"""Persistencia de la partida en la sesion del navegador."""

from __future__ import annotations

from django.http import HttpRequest

from ..mvi.state import MatchState

SESSION_KEY = "vrt.match"


def load_match(request: HttpRequest) -> MatchState:
    """Lee el estado de la partida guardado en la sesion."""
    return MatchState.from_session(request.session.get(SESSION_KEY))


def save_match(request: HttpRequest, state: MatchState) -> None:
    """Guarda el estado de la partida en la sesion."""
    request.session[SESSION_KEY] = state.to_session()


def clear_match(request: HttpRequest) -> None:
    request.session.pop(SESSION_KEY, None)
