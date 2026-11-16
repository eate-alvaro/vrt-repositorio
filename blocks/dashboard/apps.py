from __future__ import annotations

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    name = "blocks.dashboard"
    label = "dashboard"
    verbose_name = "Bloque: Panel principal"
    default_auto_field = "django.db.models.BigAutoField"
