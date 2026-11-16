"""
Etiquetas de plantilla del bloque de tema.

Iconografia: SVG monocromatico de trazo fino (stroke-width 1.5), sin emojis.
La regla del tema prohibe decoracion superflua; los indicadores visuales son
ASCII puro (`>`, `::`, `[ ]`, `-`, `*`) o estos iconos.
"""

from __future__ import annotations

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

# Trazos en una grilla de 24x24. Solo `d`, `circle` y `path`.
_ICONS: dict[str, str] = {
    "grid": '<path d="M3 3h7v7H3z"/><path d="M14 3h7v7h-7z"/><path d="M3 14h7v7H3z"/><path d="M14 14h7v7h-7z"/>',
    "crosshair": '<circle cx="12" cy="12" r="8"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/>',
    "users": '<path d="M15 19v-1a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v1"/><circle cx="8.5" cy="7" r="3"/><path d="M22 19v-1a4 4 0 0 0-3-3.87"/><path d="M16 4.13a4 4 0 0 1 0 5.74"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>',
    "power": '<path d="M12 3v9"/><path d="M18.4 6.6a9 9 0 1 1-12.8 0"/>',
    "login": '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "minus": '<path d="M5 12h14"/>',
    "refresh": '<path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/><path d="M3 21v-5h5"/>',
    "trash": '<path d="M4 7h16"/><path d="M9 7V5h6v2"/><path d="M6 7l1 13h10l1-13"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/>',
    "bolt": '<path d="M13 3 4 14h6l-1 7 9-11h-6z"/>',
    "shield": '<path d="M12 3l7 3v6c0 4-3 7-7 9-4-2-7-5-7-9V6z"/>',
    "activity": '<path d="M3 12h4l3 8 4-16 3 8h4"/>',
    "terminal": '<path d="M5 7l5 5-5 5"/><path d="M13 17h6"/>',
    "check": '<path d="M4 12l5 5L20 6"/>',
    "x": '<path d="M6 6l12 12M18 6 6 18"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/>',
    "flag": '<path d="M5 3v18"/><path d="M5 4h12l-2 4 2 4H5"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13"/><path d="M3.5 6h.01M3.5 12h.01M3.5 18h.01"/>',
    "database": '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "play": '<path d="M7 4l12 8-12 8z"/>',
    "stop": '<path d="M6 6h12v12H6z"/>',
    "chevron": '<path d="M9 6l6 6-6 6"/>',
    "layers": '<path d="M12 3 3 8l9 5 9-5z"/><path d="M3 13l9 5 9-5"/>',
    "wifi": '<path d="M5 12.5a10 10 0 0 1 14 0"/><path d="M8.5 16a5 5 0 0 1 7 0"/><path d="M12 19.5h.01"/>',
    "wifi-off": '<path d="M3 3l18 18"/><path d="M8.5 16a5 5 0 0 1 7 0"/><path d="M5 12.5a10 10 0 0 1 4-2.4"/><path d="M15 10.1a10 10 0 0 1 4 2.4"/><path d="M12 19.5h.01"/>',
    "lock": '<path d="M6 11V8a6 6 0 0 1 12 0v3"/><path d="M4 11h16v10H4z"/>',
}


@register.simple_tag
def icon(name: str, size: int = 16, stroke: float = 1.5, class_name: str = "icon") -> str:
    """Devuelve un icono SVG monocromatico de trazo fino."""
    body = _ICONS.get(name)
    if not body:
        return ""
    return mark_safe(
        f'<svg class="{escape(class_name)}" width="{int(size)}" height="{int(size)}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true" focusable="false">{body}</svg>'
    )


@register.filter
def severity_class(value: str) -> str:
    """Clase CSS segun la severidad de un evento."""
    mapping = {
        "info": "is-info",
        "success": "is-success",
        "warning": "is-warning",
        "critical": "is-critical",
        "error": "is-critical",
    }
    return mapping.get((value or "").lower(), "is-info")


@register.filter
def percent(value, total) -> int:
    """Porcentaje entero acotado a [0, 100]."""
    try:
        total = float(total)
        if total <= 0:
            return 0
        return max(0, min(100, int(round(float(value) / total * 100))))
    except (TypeError, ValueError):
        return 0


@register.simple_tag
def ascii_state(flag: bool, on: str = "ACTIVO", off: str = "INACTIVO") -> str:
    """Indicador ASCII sin emojis."""
    return f"[x] {on}" if flag else f"[ ] {off}"
