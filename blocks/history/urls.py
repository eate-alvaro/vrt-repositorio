"""Rutas del bloque de historial."""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "history"

urlpatterns = [
    path("", views.index, name="index"),
    path("vaciar/", views.clear, name="clear"),
]
