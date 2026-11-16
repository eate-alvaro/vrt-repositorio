"""
Vistas del bloque de jugadores.

Cada accion HTTP es un *Intent*: se construye el Store, se despacha y se
renderiza la *View* con el estado resultante. Las respuestas parciales
(HTMX) devuelven solo el panel del roster.
"""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods, require_POST

from core.http.context import page_context
from core.http.decorators import login_required, wants_partial
from blocks.telemetry.services.recorder import EventRecorder

from .mvi.context import RosterContext
from .mvi.intents import AddPlayer, LoadRoster, RemovePlayer, TogglePlayer
from .mvi.state import RosterState
from .mvi.store import create_roster_store
from .repositories.players import PlayerRepository

PARTIAL = "blocks/players/partials/roster_view.html"
FULL = "blocks/players/index.html"


def _context(request: HttpRequest) -> RosterContext:
    return RosterContext(
        request=request,
        repository=PlayerRepository(),
        recorder=EventRecorder(),
    )


def _render(request: HttpRequest, state: RosterState) -> HttpResponse:
    context = page_context(
        request,
        block="players",
        title="Jugadores",
        subtitle="Roster de participantes sincronizado con el nodo players.",
        state=state,
        teams=("azul", "rojo", "verde", "amarillo"),
    )
    template = PARTIAL if wants_partial(request) else FULL
    return render(request, template, context)


def _store_with_roster(request: HttpRequest):
    """Store con el roster ya cargado.

    Los intents que dependen del roster actual (alta con control de duplicados,
    baja y cambio de estado) necesitan partir del estado real, no de uno vacio.
    """
    store = create_roster_store(_context(request))
    store.dispatch(LoadRoster())
    return store


@login_required
@require_http_methods(["GET"])
def index(request: HttpRequest) -> HttpResponse:
    store = create_roster_store(_context(request))
    return _render(request, store.dispatch(LoadRoster()))


@login_required
@require_POST
def add(request: HttpRequest) -> HttpResponse:
    store = _store_with_roster(request)
    state = store.dispatch(
        AddPlayer(
            name=request.POST.get("name", ""),
            team=request.POST.get("team", "azul"),
        )
    )
    return _render(request, state)


@login_required
@require_POST
def remove(request: HttpRequest, player_id: str) -> HttpResponse:
    store = _store_with_roster(request)
    return _render(request, store.dispatch(RemovePlayer(player_id=player_id)))


@login_required
@require_POST
def toggle(request: HttpRequest, player_id: str) -> HttpResponse:
    store = _store_with_roster(request)
    return _render(request, store.dispatch(TogglePlayer(player_id=player_id)))
