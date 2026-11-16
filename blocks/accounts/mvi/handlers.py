"""
Manejadores de efectos del bloque de cuentas.

Aqui vive toda la IO: consultar Firebase, crear usuarios y escribir la sesion.
Cada manejador puede devolver un Intent de realimentacion que vuelve al reducer,
cerrando el ciclo unidireccional del MVI.
"""

from __future__ import annotations

import logging
from functools import partial
from typing import Dict, Iterable, Type, Union

from core.actor import Actor
from core.mvi import Effect, Intent, Store
from core.services.firebase import FirebaseError

from ..repositories.users import AccountsError, UsernameTaken
from .context import AuthContext
from .effects import (
    CloseSession,
    CreateAccount,
    OpenSession,
    RecordLogin,
    VerifyCredentials,
)
from .intents import AuthenticationFailed, AuthenticationSucceeded

logger = logging.getLogger("vrt.accounts")

Feedback = Union[None, Intent, Iterable[Intent]]


def create_handlers(context: AuthContext) -> Dict[Type[Effect], object]:
    """Construye el registro de manejadores ligado a la peticion actual."""
    return {
        VerifyCredentials: partial(_verify_credentials, context),
        CreateAccount: partial(_create_account, context),
        OpenSession: partial(_open_session, context),
        CloseSession: partial(_close_session, context),
        RecordLogin: partial(_record_login, context),
    }


# ---------------------------------------------------------------------------
# Acceso
# ---------------------------------------------------------------------------
def _verify_credentials(
    context: AuthContext, store: Store, effect: VerifyCredentials
) -> Feedback:
    try:
        record = context.repository.verify(effect.username, effect.password)
    except FirebaseError as exc:
        logger.warning("No se pudo verificar credenciales: %s", exc)
        return AuthenticationFailed(
            message=(
                "No se pudo consultar Firebase Realtime Database. "
                "Revisa la conexion y las reglas del nodo `users`."
            ),
            code="backend_unavailable",
        )

    if record is None:
        return AuthenticationFailed(
            message="Usuario o contrasena incorrectos.",
            code="invalid_credentials",
        )

    actor = Actor(
        username=record.username,
        display_name=record.label,
        role=record.role,
    )
    return AuthenticationSucceeded(actor=actor, remember=effect.remember)


# ---------------------------------------------------------------------------
# Registro
# ---------------------------------------------------------------------------
def _create_account(context: AuthContext, store: Store, effect: CreateAccount) -> Feedback:
    try:
        record = context.repository.create(
            effect.username,
            effect.password,
            display_name=effect.display_name,
            role=effect.role,
        )
    except UsernameTaken:
        return AuthenticationFailed(
            message=f"El usuario '{effect.username}' ya esta registrado.",
            code="username_taken",
        )
    except AccountsError as exc:
        return AuthenticationFailed(message=str(exc), code="invalid_registration")
    except FirebaseError as exc:
        logger.warning("No se pudo crear la cuenta: %s", exc)
        return AuthenticationFailed(
            message=(
                "No se pudo escribir en Firebase Realtime Database. "
                "Verifica las reglas del nodo `users`."
            ),
            code="backend_unavailable",
        )

    actor = Actor(
        username=record.username,
        display_name=record.label,
        role=record.role,
    )
    return AuthenticationSucceeded(actor=actor, remember=True, created=True)


# ---------------------------------------------------------------------------
# Sesion
# ---------------------------------------------------------------------------
def _open_session(context: AuthContext, store: Store, effect: OpenSession) -> Feedback:
    from core.http.middleware import write_actor

    write_actor(context.request, effect.actor, remember=effect.remember)
    return None


def _close_session(context: AuthContext, store: Store, effect: CloseSession) -> Feedback:
    from core.http.middleware import write_actor

    write_actor(context.request, None)
    context.session.flush()
    return None


def _record_login(context: AuthContext, store: Store, effect: RecordLogin) -> Feedback:
    context.repository.touch_last_login(effect.username)
    return None
