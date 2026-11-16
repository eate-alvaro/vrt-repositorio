"""Vistas del bloque de historial."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods, require_POST

from core.http.context import page_context
from core.http.decorators import login_required, wants_partial

from .mvi.handlers import HistoryContext
from .mvi.intents import ClearHistory, LoadHistory, SetSeverityFilter
from .mvi.state import FILTERS, HistoryState
from .mvi.store import create_history_store

PARTIAL = "blocks/history/partials/history_view.html"
FULL = "blocks/history/index.html"
DEFAULT_LIMIT = 200


def _render(request: HttpRequest, state: HistoryState) -> HttpResponse:
    context = page_context(
        request,
        block="history",
        title="Historial de eventos",
        subtitle="Telemetria capturada en el nodo events: disparos, impactos, roster y partidas.",
        state=state,
        filters=FILTERS,
    )
    template = PARTIAL if wants_partial(request) else FULL
    return render(request, template, context)


@login_required
@require_http_methods(["GET"])
def index(request: HttpRequest) -> HttpResponse:
    store = create_history_store(HistoryContext())
    store.dispatch(LoadHistory(limit=DEFAULT_LIMIT))
    state = store.dispatch(SetSeverityFilter(severity=request.GET.get("severity", "todos")))
    return _render(request, state)


@login_required
@require_POST
def clear(request: HttpRequest) -> HttpResponse:
    store = create_history_store(HistoryContext())
    state = store.dispatch(ClearHistory())
    state = store.dispatch(SetSeverityFilter(severity=request.POST.get("severity", "todos")))
    return _render(request, state)
