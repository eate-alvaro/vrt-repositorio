"""
Reducer del bloque de cuentas.

Funcion pura: recibe el estado y un intent, y devuelve el estado nuevo junto
con la lista de efectos a ejecutar. No toca la red, la sesion ni la base de
datos.
"""

from __future__ import annotations

from typing import Sequence, Tuple

from core.mvi import Effect, Intent

from .effects import (
    CloseSession,
    CreateAccount,
    OpenSession,
    RecordLogin,
    VerifyCredentials,
)
from .intents import (
    AuthenticationFailed,
    AuthenticationSucceeded,
    RequestLogout,
    SubmitLogin,
    SubmitRegistration,
)
from .state import AuthState


def reduce_auth(state: AuthState, intent: Intent) -> Tuple[AuthState, Sequence[Effect]]:
    # -- acceso ------------------------------------------------------------
    if isinstance(intent, SubmitLogin):
        username = (intent.username or "").strip()
        if not username or not intent.password:
            return (
                state.evolve(
                    mode="login",
                    status="failed",
                    error="Usuario y contrasena son obligatorios.",
                    error_code="missing_fields",
                ),
                (),
            )
        return (
            state.evolve(
                mode="login",
                status="processing",
                username=username,
                display_name="",
                remember=intent.remember,
                error="",
                error_code="",
                notice="",
                attempts=state.attempts + 1,
            ),
            (
                VerifyCredentials(
                    username=username,
                    password=intent.password,
                    remember=intent.remember,
                ),
            ),
        )

    # -- registro ----------------------------------------------------------
    if isinstance(intent, SubmitRegistration):
        username = (intent.username or "").strip()
        if not username or not intent.password:
            return (
                state.evolve(
                    mode="register",
                    status="failed",
                    error="Usuario y contrasena son obligatorios.",
                    error_code="missing_fields",
                ),
                (),
            )
        if len(intent.password) < 4:
            return (
                state.evolve(
                    mode="register",
                    status="failed",
                    error="La contrasena debe tener al menos 4 caracteres.",
                    error_code="weak_password",
                ),
                (),
            )
        return (
            state.evolve(
                mode="register",
                status="processing",
                username=username,
                display_name=(intent.display_name or "").strip(),
                error="",
                error_code="",
                notice="",
            ),
            (
                CreateAccount(
                    username=username,
                    password=intent.password,
                    display_name=(intent.display_name or "").strip(),
                    role=intent.role,
                ),
            ),
        )

    # -- resultados --------------------------------------------------------
    if isinstance(intent, AuthenticationSucceeded):
        return (
            state.evolve(
                status="authenticated",
                actor=intent.actor,
                username=intent.actor.username,
                display_name=intent.actor.display_name,
                error="",
                error_code="",
                notice="Cuenta creada. Sesion iniciada." if intent.created else "",
            ),
            (
                OpenSession(actor=intent.actor, remember=intent.remember),
                RecordLogin(username=intent.actor.username),
            ),
        )

    if isinstance(intent, AuthenticationFailed):
        return (
            state.evolve(
                status="failed",
                actor=None,
                error=intent.message,
                error_code=intent.code,
            ),
            (),
        )

    # -- cierre de sesion --------------------------------------------------
    if isinstance(intent, RequestLogout):
        return (
            state.evolve(status="idle", actor=None, notice=""),
            (CloseSession(),),
        )

    return state, ()
