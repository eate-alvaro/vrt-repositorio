"""Estado inmutable del bloque de cuentas."""

from __future__ import annotations

from dataclasses import dataclass

from core.actor import Actor
from core.mvi import State


@dataclass(frozen=True)
class AuthState(State):
    """Estado del formulario de acceso y de la sesion."""

    mode: str = "login"  # login | register
    status: str = "idle"  # idle | processing | failed | authenticated
    actor: Actor | None = None
    username: str = ""
    display_name: str = ""
    remember: bool = False
    error: str = ""
    error_code: str = ""
    notice: str = ""
    attempts: int = 0

    @property
    def is_authenticated(self) -> bool:
        return self.status == "authenticated" and self.actor is not None

    @property
    def is_failed(self) -> bool:
        return self.status == "failed"
