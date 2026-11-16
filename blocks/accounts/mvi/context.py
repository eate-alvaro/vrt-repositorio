"""Contexto de ejecucion del bloque de cuentas (dependencias inyectadas)."""

from __future__ import annotations

from dataclasses import dataclass

from django.http import HttpRequest

from blocks.accounts.repositories.users import UserRepository


@dataclass(frozen=True)
class AuthContext:
    """Dependencias que necesitan los manejadores de efectos."""

    request: HttpRequest
    repository: UserRepository

    @property
    def session(self):
        return self.request.session
