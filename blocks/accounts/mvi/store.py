"""Fabrica del Store MVI del bloque de cuentas."""

from __future__ import annotations

from core.mvi import Store, create_store

from .context import AuthContext
from .handlers import create_handlers
from .reducer import reduce_auth
from .state import AuthState


def create_auth_store(
    context: AuthContext, state: AuthState | None = None
) -> Store[AuthState]:
    """Construye el Store del bloque con el estado inicial indicado."""
    return create_store(state or AuthState(), reduce_auth, create_handlers(context))
