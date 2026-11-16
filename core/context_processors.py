"""Procesadores de contexto del nucleo."""

from __future__ import annotations

from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone


def app_context(request: HttpRequest) -> dict:
    """Metadatos de la aplicacion y estado de sesion disponibles en plantillas."""
    host = urlparse(settings.FIREBASE_DB_URL).hostname or "firebaseio"
    return {
        "actor": getattr(request, "actor", None),
        "now": timezone.localtime(),
        "firebase_host": host,
        "firebase_url": settings.FIREBASE_DB_URL,
        "app_version": settings.VRT_APP_VERSION,
    }
