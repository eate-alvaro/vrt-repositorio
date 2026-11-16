from __future__ import annotations

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "blocks.accounts"
    label = "accounts"
    verbose_name = "Bloque: Cuentas"
    default_auto_field = "django.db.models.BigAutoField"
