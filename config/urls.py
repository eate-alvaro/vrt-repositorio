"""
Enrutado raiz.

Cada bloque funcional publica su propio modulo de rutas con su namespace,
de modo que la estructura de URLs refleja la arquitectura por bloques.
"""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("", include("blocks.dashboard.urls")),
    path("cuenta/", include("blocks.accounts.urls")),
    path("simulacion/", include("blocks.simulation.urls")),
    path("jugadores/", include("blocks.players.urls")),
    path("historial/", include("blocks.history.urls")),
]
