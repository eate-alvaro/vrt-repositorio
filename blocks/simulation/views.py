"""
Vistas del bloque de simulacion.

`accion/` es el punto unico donde entran los intents de la partida: traduce el
campo `action` del formulario a un Intent tipado, lo despacha y devuelve el
panel actualizado (completo o parcial segun HTMX).
"""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from core.http.context import page_context
from core.http.decorators import login_required, wants_partial
from blocks.telemetry.services.recorder import EventRecorder

from .mvi.context import MatchContext
from .mvi.intents import FinishMatch, RegisterHit, ResetMatch, Shoot, StartMatch
from .mvi.state import MatchState
from .mvi.store import create_match_store
from .repositories.sessions import SessionRepository
from .services.session import load_match

PARTIAL = "blocks/simulation/partials/match_view.html"
FULL = "blocks/simulation/index.html"


def _context(request: HttpRequest) -> MatchContext:
    return MatchContext(
        request=request,
        sessions=SessionRepository(),
        recorder=EventRecorder(),
    )


def _render(request: HttpRequest, state: MatchState) -> HttpResponse:
    context = page_context(
        request,
        block="simulation",
        title="Simulacion",
        subtitle="Maquina de estados MVI: cada boton es un Intent y cada evento queda en la telemetria.",
        state=state,
    )
    template = PARTIAL if wants_partial(request) else FULL
    return render(request, template, context)


def _now() -> str:
    return timezone.now().isoformat(timespec="seconds")


def _build_intent(action: str):
    """Traduce la accion del formulario a un Intent tipado."""
    if action == "start":
        stamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
        return StartMatch(match_id=f"M-{stamp}", started_at=_now())
    if action == "shoot":
        return Shoot()
    if action == "hit":
        return RegisterHit(received_at=_now())
    if action == "finish":
        return FinishMatch(finished_at=_now())
    if action == "reset":
        return ResetMatch()
    return None


@login_required
@require_http_methods(["GET"])
def index(request: HttpRequest) -> HttpResponse:
    return _render(request, load_match(request))


@login_required
@require_POST
def action(request: HttpRequest) -> HttpResponse:
    intent = _build_intent(request.POST.get("action", ""))
    state = load_match(request)
    if intent is not None:
        store = create_match_store(_context(request), state)
        state = store.dispatch(intent)
    return _render(request, state)
