"""Helpers de contexto de plantilla para las vistas de cada bloque."""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest


def page_context(
    request: HttpRequest,
    *,
    block: str | None,
    title: str,
    subtitle: str = "",
    **extra: Any,
) -> dict[str, Any]:
    """Contexto base de una pagina del workspace."""
    context: dict[str, Any] = {
        "active_block": block,
        "page_title": title,
        "page_subtitle": subtitle,
        "actor": getattr(request, "actor", None),
    }
    context.update(extra)
    return context
