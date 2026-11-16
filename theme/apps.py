from __future__ import annotations

from django.apps import AppConfig


class ThemeConfig(AppConfig):
    name = "theme"
    label = "theme"
    verbose_name = "Bloque: Tema Tokyo Night"
    default_auto_field = "django.db.models.BigAutoField"
