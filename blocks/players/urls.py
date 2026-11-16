"""Rutas del bloque de jugadores."""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "players"

urlpatterns = [
    path("", views.index, name="index"),
    path("agregar/", views.add, name="add"),
    path("<str:player_id>/estado/", views.toggle, name="toggle"),
    path("<str:player_id>/eliminar/", views.remove, name="remove"),
]
