"""Efectos declarativos del bloque de cuentas."""

from __future__ import annotations

from dataclasses import dataclass

from core.actor import Actor
from core.mvi import Effect


@dataclass(frozen=True)
class VerifyCredentials(Effect):
    """Consultar el nodo `users` y validar la contrasena."""

    username: str
    password: str
    remember: bool = False


@dataclass(frozen=True)
class CreateAccount(Effect):
    """Crear un usuario nuevo en el nodo `users`."""

    username: str
    password: str
    display_name: str = ""
    role: str = "operator"


@dataclass(frozen=True)
class OpenSession(Effect):
    """Persistir el actor en la sesion de Django."""

    actor: Actor
    remember: bool = False


@dataclass(frozen=True)
class CloseSession(Effect):
    """Eliminar el actor de la sesion de Django."""


@dataclass(frozen=True)
class RecordLogin(Effect):
    """Actualizar la marca `last_login` del usuario."""

    username: str
