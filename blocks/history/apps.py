from __future__ import annotations

from django.apps import AppConfig


class HistoryConfig(AppConfig):
    name = "blocks.history"
    label = "history"
    verbose_name = "Bloque: Historial"
    default_auto_field = "django.db.models.BigAutoField"
