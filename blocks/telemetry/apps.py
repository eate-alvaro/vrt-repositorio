from __future__ import annotations

from django.apps import AppConfig


class TelemetryConfig(AppConfig):
    name = "blocks.telemetry"
    label = "telemetry"
    verbose_name = "Bloque: Telemetria"
    default_auto_field = "django.db.models.BigAutoField"
