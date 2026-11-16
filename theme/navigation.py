"""
Navegacion global del workspace.

Cada entrada corresponde a un bloque funcional con interfaz. El bloque de tema
es el unico responsable de como se presenta la navegacion.
"""

from __future__ import annotations

from typing import Any

from django.urls import reverse


def navigation() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = [
        {
            "key": "dashboard",
            "label": "Panel principal",
            "url_name": "dashboard:index",
            "icon": "grid",
            "hint": "resumen",
        },
        {
            "key": "simulation",
            "label": "Simulacion",
            "url_name": "simulation:index",
            "icon": "crosshair",
            "hint": "partida",
        },
        {
            "key": "players",
            "label": "Jugadores",
            "url_name": "players:index",
            "icon": "users",
            "hint": "roster",
        },
        {
            "key": "history",
            "label": "Historial",
            "url_name": "history:index",
            "icon": "clock",
            "hint": "telemetria",
        },
        {
            "key": "about",
            "label": "Proyecto",
            "url_name": "dashboard:about",
            "icon": "info",
            "hint": "documentacion",
        },
    ]
    for item in items:
        item["url"] = reverse(item["url_name"])
    return items
