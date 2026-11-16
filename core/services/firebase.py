"""
Cliente minimo para Firebase Realtime Database usando su API REST.

No requiere SDK: Realtime Database expone cada nodo como JSON en

    {FIREBASE_DB_URL}/<ruta>.json

lo que permite GET / PUT / PATCH / POST / DELETE desde Python con `requests`.
"""

from __future__ import annotations

import logging
from typing import Any, Optional
from urllib.parse import quote, urlencode

import requests
from django.conf import settings

logger = logging.getLogger("vrt.firebase")


class FirebaseError(RuntimeError):
    """Error de comunicacion o de reglas de la Realtime Database."""


class FirebaseRealtimeDB:
    """Envoltorio REST sobre un nodo raiz de Realtime Database."""

    def __init__(
        self,
        base_url: str,
        auth_token: str | None = None,
        timeout: float = 8.0,
    ) -> None:
        self.base_url = (base_url or "").rstrip("/")
        self.auth_token = auth_token or None
        self.timeout = timeout
        self._session = requests.Session()

    # -- utilidades ---------------------------------------------------------
    def _url(self, path: str, params: dict | None = None) -> str:
        clean = (path or "").strip("/")
        url = f"{self.base_url}/{clean}.json" if clean else f"{self.base_url}/.json"
        query: dict[str, str] = dict(params or {})
        if self.auth_token:
            query["auth"] = self.auth_token
        if query:
            url = f"{url}?{urlencode(query)}"
        return url

    def _request(
        self, method: str, path: str, payload: Any = None, params: dict | None = None
    ) -> Any:
        url = self._url(path, params)
        try:
            response = self._session.request(
                method, url, json=payload, timeout=self.timeout
            )
        except requests.RequestException as exc:
            logger.warning("Fallo de red contra Firebase (%s %s): %s", method, path, exc)
            raise FirebaseError(f"No se pudo conectar con Firebase: {exc}") from exc

        if response.status_code >= 400:
            logger.warning(
                "Firebase respondio %s en %s %s: %s",
                response.status_code,
                method,
                path,
                response.text[:200],
            )
            raise FirebaseError(
                f"Firebase respondio {response.status_code} en {path}: {response.text[:200]}"
            )

        if not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            return response.text

    # -- operaciones --------------------------------------------------------
    def get(self, path: str = "", params: dict | None = None) -> Any:
        return self._request("GET", path, params=params)

    def put(self, path: str, data: Any) -> Any:
        return self._request("PUT", path, data)

    def patch(self, path: str, data: Any) -> Any:
        return self._request("PATCH", path, data)

    def post(self, path: str, data: Any) -> Any:
        return self._request("POST", path, data)

    def delete(self, path: str = "") -> Any:
        return self._request("DELETE", path)

    def keys(self, path: str = "") -> list[str]:
        """Devuelve solo las claves de un nodo (consulta superficial)."""
        payload = self._request("GET", path, params={"shallow": "true"}) or {}
        return list(payload.keys()) if isinstance(payload, dict) else []

    def health(self) -> tuple[bool, str]:
        """Comprueba la conectividad. Devuelve (ok, detalle)."""
        try:
            response = self._session.get(self._url(""), timeout=self.timeout)
        except requests.RequestException as exc:
            return False, f"sin conexion: {exc}"
        if response.status_code >= 400:
            return False, f"HTTP {response.status_code}: {response.text[:120]}"
        return True, f"HTTP {response.status_code}"


_client: Optional[FirebaseRealtimeDB] = None


def get_client() -> FirebaseRealtimeDB:
    """Cliente compartido (perezoso) configurado desde settings."""
    global _client
    if _client is None:
        _client = FirebaseRealtimeDB(
            base_url=settings.FIREBASE_DB_URL,
            auth_token=settings.FIREBASE_DB_SECRET or None,
            timeout=settings.FIREBASE_TIMEOUT,
        )
    return _client


def reset_client() -> None:
    """Descarta el cliente compartido (util en pruebas)."""
    global _client
    _client = None
