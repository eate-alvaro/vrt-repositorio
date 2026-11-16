"""Rutas del bloque de cuentas."""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("entrar/", views.login_view, name="login"),
    path("registro/", views.register_view, name="register"),
    path("salir/", views.logout_view, name="logout"),
]
