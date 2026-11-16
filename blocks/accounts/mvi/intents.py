"""Intents del bloque de cuentas: lo que el usuario pretende hacer."""

from __future__ import annotations

from dataclasses import dataclass

from core.actor import Actor
from core.mvi import Intent


@dataclass(frozen=True)
class SubmitLogin(Intent):
    """El usuario envio el formulario de acceso."""

    username: str
    password: str
    remember: bool = False


@dataclass(frozen=True)
class SubmitRegistration(Intent):
    """El usuario solicito crear una cuenta."""

    username: str
    password: str
    display_name: str = ""
    role: str = "operator"


@dataclass(frozen=True)
class RequestLogout(Intent):
    """El usuario solicito cerrar sesion."""


@dataclass(frozen=True)
class AuthenticationSucceeded(Intent):
    """Realimentacion: las credenciales fueron validas (o la cuenta creada)."""

    actor: Actor
    remember: bool = False
    created: bool = False


@dataclass(frozen=True)
class AuthenticationFailed(Intent):
    """Realimentacion: las credenciales fueron rechazadas."""

    message: str
    code: str = "invalid_credentials"
