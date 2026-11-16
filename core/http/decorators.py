"""Decoradores HTTP compartidos por los bloques."""

from __future__ import annotations

from functools import wraps
from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode, url_has_allowed_host_and_scheme


def login_required(view: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    """Redirige al login del bloque `accounts` si no hay actor en sesion."""

    @wraps(view)
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if getattr(request, "actor", None) is None:
            login_url = reverse("accounts:login")
            target = request.get_full_path()
            if target and target != "/":
                login_url = f"{login_url}?{urlencode({'next': target})}"
            return redirect(login_url)
        return view(request, *args, **kwargs)

    return wrapper


def safe_redirect_target(request: HttpRequest, candidate: str | None, fallback: str) -> str:
    """Valida un `next` para evitar redirecciones abiertas."""
    if candidate and url_has_allowed_host_and_scheme(
        url=candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return fallback


def wants_partial(request: HttpRequest) -> bool:
    """True si la peticion espera un fragmento (HTMX o fetch parcial)."""
    return request.headers.get("HX-Request") == "true" or request.GET.get("partial") == "1"
