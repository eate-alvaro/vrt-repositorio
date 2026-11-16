"""Procesador de contexto del bloque de tema."""

from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest

from .navigation import navigation


def theme_context(request: HttpRequest) -> dict:
    return {
        "app_name": settings.VRT_APP_NAME,
        "app_tagline": settings.VRT_APP_TAGLINE,
        "app_version": settings.VRT_APP_VERSION,
        "demo_mode": settings.VRT_DEMO_MODE,
        "theme_name": "TOKYO NIGHT",
        "nav_blocks": navigation(),
    }
