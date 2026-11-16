"""Rutas del bloque de simulacion."""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "simulation"

urlpatterns = [
    path("", views.index, name="index"),
    path("accion/", views.action, name="action"),
]
