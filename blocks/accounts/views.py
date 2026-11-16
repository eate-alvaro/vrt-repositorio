"""
Vistas del bloque de cuentas.

La vista cumple el papel de *Intent dispatcher*: recibe la peticion HTTP,
construye el Store MVI, despacha el intent correspondiente y renderiza la
*View* con el estado resultante.
"""

from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from core.http.decorators import safe_redirect_target

from .mvi.context import AuthContext
from .mvi.intents import RequestLogout, SubmitLogin, SubmitRegistration
from .mvi.state import AuthState
from .mvi.store import create_auth_store
from .repositories.users import UserRepository


def _auth_context(request: HttpRequest, state: AuthState) -> dict:
    return {
        "active_block": None,
        "block_title": "acceso" if state.mode == "login" else "registro",
        "state": state,
        "next": request.POST.get("next") or request.GET.get("next", ""),
    }


def _build_context(request: HttpRequest) -> AuthContext:
    return AuthContext(request=request, repository=UserRepository())


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    """Intent: iniciar sesion contra el nodo `users` de Realtime Database."""
    if request.actor is not None:
        return redirect("dashboard:index")

    if request.method == "POST":
        store = create_auth_store(_build_context(request))
        state = store.dispatch(
            SubmitLogin(
                username=request.POST.get("username", ""),
                password=request.POST.get("password", ""),
                remember=bool(request.POST.get("remember")),
            )
        )

        if state.is_authenticated:
            target = safe_redirect_target(
                request, request.POST.get("next"), "dashboard:index"
            )
            messages.success(request, f"Sesion iniciada como {state.actor.label}.")
            return redirect(target)

        return render(
            request,
            "blocks/accounts/login.html",
            _auth_context(request, state),
            status=400,
        )

    state = AuthState(mode="login", username=request.GET.get("username", ""))
    return render(request, "blocks/accounts/login.html", _auth_context(request, state))


@require_http_methods(["GET", "POST"])
def register_view(request: HttpRequest) -> HttpResponse:
    """Intent: crear una cuenta nueva en el nodo `users`."""
    if request.actor is not None:
        return redirect("dashboard:index")

    if request.method == "POST":
        store = create_auth_store(_build_context(request))
        state = store.dispatch(
            SubmitRegistration(
                username=request.POST.get("username", ""),
                password=request.POST.get("password", ""),
                display_name=request.POST.get("display_name", ""),
                role="operator",
            )
        )

        if state.is_authenticated:
            messages.success(request, "Cuenta creada. Sesion iniciada.")
            return redirect("dashboard:index")

        return render(
            request,
            "blocks/accounts/register.html",
            _auth_context(request, state),
            status=400,
        )

    state = AuthState(mode="register")
    return render(request, "blocks/accounts/register.html", _auth_context(request, state))


@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    """Intent: cerrar sesion."""
    store = create_auth_store(_build_context(request))
    store.dispatch(RequestLogout())
    messages.info(request, "Sesion cerrada correctamente.")
    return redirect("accounts:login")
