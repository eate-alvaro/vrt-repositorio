"""Middleware que expone el actor autenticado en `request.actor`."""

from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse

from core.actor import Actor

SESSION_ACTOR_KEY = "vrt.actor"


def read_actor(request: HttpRequest) -> Actor | None:
    """Lee el actor desde la sesion de Django."""
    try:
        payload = request.session.get(SESSION_ACTOR_KEY)
    except AttributeError:  # sesiones no inicializadas
        return None
    return Actor.from_session(payload) if payload else None


def write_actor(request: HttpRequest, actor: Actor | None, *, remember: bool = False) -> None:
    """Guarda (o elimina) el actor en la sesion."""
    if actor is None:
        request.session.pop(SESSION_ACTOR_KEY, None)
    else:
        request.session[SESSION_ACTOR_KEY] = actor.to_session()
    if remember:
        request.session.set_expiry(60 * 60 * 24 * 14)
    else:
        request.session.set_expiry(0)


class ActorMiddleware:
    """Anade `request.actor` a cada peticion (soporte MVI)."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.actor = read_actor(request)  # type: ignore[attr-defined]
        return self.get_response(request)
