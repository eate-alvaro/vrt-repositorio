from __future__ import annotations

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"
    label = "core"
    verbose_name = "Nucleo MVI"
    default_auto_field = "django.db.models.BigAutoField"
