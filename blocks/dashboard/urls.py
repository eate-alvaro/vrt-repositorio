"""Rutas del bloque del panel principal."""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("proyecto/", views.about, name="about"),
]
