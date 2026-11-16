from __future__ import annotations

from django.apps import AppConfig


class SimulationConfig(AppConfig):
    name = "blocks.simulation"
    label = "simulation"
    verbose_name = "Bloque: Simulacion"
    default_auto_field = "django.db.models.BigAutoField"
