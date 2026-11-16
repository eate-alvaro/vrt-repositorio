"""Vistas del bloque del panel principal."""

from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.http.context import page_context
from core.http.decorators import login_required, wants_partial

from .mvi.handlers import DashboardContext
from .mvi.intents import LoadDashboard
from .mvi.state import DashboardState
from .mvi.store import create_dashboard_store

PARTIAL = "blocks/dashboard/partials/dashboard_view.html"
FULL = "blocks/dashboard/index.html"


def _render(request: HttpRequest, state: DashboardState) -> HttpResponse:
    context = page_context(
        request,
        block="dashboard",
        title="Panel principal",
        subtitle="Centro de control de la simulacion de paintball en entornos controlados.",
        state=state,
    )
    template = PARTIAL if wants_partial(request) else FULL
    return render(request, template, context)


@login_required
@require_http_methods(["GET"])
def index(request: HttpRequest) -> HttpResponse:
    store = create_dashboard_store(DashboardContext())
    return _render(request, store.dispatch(LoadDashboard()))


@login_required
@require_http_methods(["GET"])
def about(request: HttpRequest) -> HttpResponse:
    context = page_context(
        request,
        block="about",
        title="Acerca del proyecto",
        subtitle="Documentacion tecnica del modelo de realidad virtual e IoT.",
        firebase_url=settings.FIREBASE_DB_URL,
    )
    return render(request, "blocks/dashboard/about.html", context)
