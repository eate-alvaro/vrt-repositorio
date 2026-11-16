"""
Repositorio de usuarios sobre Firebase Realtime Database.

Estructura del nodo `users`:

    users/
      jugador01/
        username:      "jugador01"
        display_name:  "Jugador 01"
        role:          "operator" | "admin"
        active:        true
        password_hash: "pbkdf2_sha256$..."
        created_at:    "2026-01-01T10:00:00-04:00"
        last_login:    "2026-01-02T18:22:10-04:00"

La contrasena nunca se guarda en claro: se almacena el hash generado por
Django (`make_password`) y se verifica con `check_password`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any, Optional

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone

from core.services.firebase import FirebaseError, get_client

_KEY_INVALID = re.compile(r"[^a-z0-9_-]+")


class AccountsError(RuntimeError):
    """Error de dominio del bloque de cuentas."""


class UsernameTaken(AccountsError):
    """El nombre de usuario ya existe en el nodo `users`."""


def user_key(username: str) -> str:
    """Convierte un usuario en una clave valida de Realtime Database.

    Realtime Database prohibe `. $ # [ ] /` en las claves, por lo que se
    normaliza el identificador a `[a-z0-9_-]`.
    """
    normalized = (username or "").strip().lower()
    normalized = normalized.replace("@", "-at-").replace(".", "-")
    key = _KEY_INVALID.sub("-", normalized).strip("-")
    return key[:120] or "anonimo"


@dataclass(frozen=True)
class UserRecord:
    """Registro de usuario tal como vive en Firebase."""

    username: str
    display_name: str = ""
    role: str = "operator"
    active: bool = True
    password_hash: str = ""
    created_at: str = ""
    last_login: str = ""

    @property
    def label(self) -> str:
        return self.display_name or self.username

    def to_payload(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role,
            "active": self.active,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "last_login": self.last_login,
        }

    @classmethod
    def from_payload(cls, payload: dict | None) -> "UserRecord":
        payload = payload or {}
        return cls(
            username=str(payload.get("username", "")),
            display_name=str(payload.get("display_name", "")),
            role=str(payload.get("role", "operator")),
            active=bool(payload.get("active", True)),
            password_hash=str(payload.get("password_hash", "")),
            created_at=str(payload.get("created_at", "")),
            last_login=str(payload.get("last_login", "")),
        )


class UserRepository:
    """Acceso al nodo de usuarios de Realtime Database."""

    def __init__(self, client=None, node: str | None = None) -> None:
        self._client = client or get_client()
        self._node = node or settings.FIREBASE_USERS_NODE

    # -- rutas --------------------------------------------------------------
    def _path(self, username: str = "") -> str:
        key = user_key(username) if username else ""
        return f"{self._node}/{key}" if key else self._node

    # -- lectura ------------------------------------------------------------
    def get(self, username: str) -> Optional[UserRecord]:
        payload = self._client.get(self._path(username))
        if not payload:
            return None
        record = UserRecord.from_payload(payload)
        if not record.username:
            record = replace(record, username=username)
        return record

    def exists(self, username: str) -> bool:
        return self.get(username) is not None

    def list_all(self) -> list[UserRecord]:
        payload = self._client.get(self._node) or {}
        records: list[UserRecord] = []
        if isinstance(payload, dict):
            for key, value in payload.items():
                record = UserRecord.from_payload(value)
                if not record.username:
                    record = replace(record, username=key)
                records.append(record)
        return sorted(records, key=lambda r: r.username)

    def count(self) -> int:
        return len(self.list_all())

    # -- escritura ----------------------------------------------------------
    def create(
        self,
        username: str,
        password: str,
        *,
        display_name: str = "",
        role: str = "operator",
    ) -> UserRecord:
        username = (username or "").strip()
        if not username:
            raise AccountsError("El nombre de usuario es obligatorio.")
        if not password:
            raise AccountsError("La contrasena es obligatoria.")
        if self.exists(username):
            raise UsernameTaken(f"El usuario '{username}' ya esta registrado.")

        now = timezone.now().isoformat(timespec="seconds")
        record = UserRecord(
            username=username,
            display_name=(display_name or username).strip(),
            role=role or "operator",
            active=True,
            password_hash=make_password(password),
            created_at=now,
            last_login="",
        )
        self._client.put(self._path(username), record.to_payload())
        return record

    def touch_last_login(self, username: str) -> None:
        """Actualiza la marca de ultimo acceso (mejor esfuerzo)."""
        try:
            self._client.patch(
                self._path(username),
                {"last_login": timezone.now().isoformat(timespec="seconds")},
            )
        except FirebaseError:
            # No debe impedir el inicio de sesion.
            pass

    def verify(self, username: str, password: str) -> Optional[UserRecord]:
        """Devuelve el usuario si las credenciales son validas."""
        if not username or not password:
            return None
        record = self.get(username)
        if record is None or not record.active or not record.password_hash:
            return None
        if not check_password(password, record.password_hash):
            return None
        return record

    def delete(self, username: str) -> None:
        self._client.delete(self._path(username))
