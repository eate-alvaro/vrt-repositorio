"""Comando: verifica la conectividad con Firebase Realtime Database."""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.conf import settings

from core.services.firebase import FirebaseError, get_client


class Command(BaseCommand):
    help = "Comprueba la conexion con Firebase Realtime Database y cuenta los nodos principales."

    NODES = ("users", "players", "sessions", "events")

    def handle(self, *args, **options) -> None:
        client = get_client()
        self.stdout.write(f"URL         : {settings.FIREBASE_DB_URL}")
        self.stdout.write(f"Timeout     : {settings.FIREBASE_TIMEOUT} s")
        self.stdout.write(
            f"Credencial  : {'token configurado' if settings.FIREBASE_DB_SECRET else 'sin token (acceso publico)'}"
        )
        self.stdout.write("-" * 58)

        ok, detail = client.health()
        if ok:
            self.stdout.write(self.style.SUCCESS(f"[OK]   conexion establecida ({detail})"))
        else:
            self.stdout.write(self.style.ERROR(f"[FALLO] {detail}"))
            self.stdout.write(
                "Revisa la conexion a internet, la URL de la base de datos y las reglas de lectura."
            )
            return

        self.stdout.write("-" * 58)
        for node in self.NODES:
            try:
                count = len(client.keys(node))
            except FirebaseError as exc:
                self.stdout.write(self.style.WARNING(f"[AVISO] {node:<9} inaccesible: {exc}"))
                continue
            self.stdout.write(f"[INFO] {node:<9} {count} registro(s)")

        self.stdout.write("-" * 58)
        self.stdout.write(self.style.SUCCESS("Diagnostico completado."))
