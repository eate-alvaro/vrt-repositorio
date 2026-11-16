"""
Comando: siembra datos de demostracion en Firebase Realtime Database.

Crea usuarios de acceso, un roster de ejemplo y algunos eventos de telemetria
para que la plataforma sea utilizable desde el primer arranque.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.services.firebase import FirebaseError, get_client
from blocks.accounts.repositories.users import AccountsError, UserRepository
from blocks.players.repositories.players import PlayerRepository
from blocks.telemetry.repositories.events import EventRepository
from blocks.telemetry.services.recorder import EventRecorder

DEMO_USERS = (
    {"username": "admin", "password": "admin1234", "display_name": "Administrador", "role": "admin"},
    {"username": "jugador01", "password": "1234", "display_name": "Jugador 01", "role": "operator"},
    {"username": "jugador02", "password": "1234", "display_name": "Jugador 02", "role": "operator"},
)

DEMO_PLAYERS = (
    {"name": "Ana Quispe", "team": "azul"},
    {"name": "Luis Mamani", "team": "azul"},
    {"name": "Carla Rojas", "team": "rojo"},
    {"name": "Diego Vargas", "team": "rojo"},
    {"name": "Elena Siles", "team": "verde"},
)

DEMO_EVENTS = (
    ("partida:inicio", "Partida M-DEMO-001 iniciada.", "success"),
    ("disparo", "Disparo detectado. Municion restante: 29.", "info"),
    ("disparo", "Disparo detectado. Municion restante: 28.", "info"),
    ("impacto", "Impacto recibido. Vida restante: 80.", "warning"),
    ("roster:alta", "Jugador 'Elena Siles' agregado al equipo verde.", "info"),
    ("sensor:lectura", "ESP32 reporto 12 impactos en el chaleco 03.", "info"),
)


class Command(BaseCommand):
    help = "Crea usuarios, jugadores y eventos de demostracion en Realtime Database."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Vacia los nodos players y events antes de sembrar (no borra users).",
        )
        parser.add_argument(
            "--events-only",
            action="store_true",
            help="Siembra unicamente eventos de telemetria.",
        )

    def handle(self, *args, **options) -> None:
        client = get_client()
        ok, detail = client.health()
        if not ok:
            self.stderr.write(self.style.ERROR(f"Sin conexion con Firebase: {detail}"))
            return

        if options["reset"]:
            self.stdout.write("Vaciando nodos players y events...")
            for node in ("players", "events"):
                try:
                    client.delete(node)
                except FirebaseError as exc:
                    self.stderr.write(self.style.WARNING(f"No se pudo vaciar {node}: {exc}"))

        if not options["events_only"]:
            self._seed_users()
            self._seed_players()

        self._seed_events()

        self.stdout.write("-" * 58)
        self.stdout.write(self.style.SUCCESS("Datos de demostracion sembrados."))
        self.stdout.write("Usuarios de acceso:")
        for user in DEMO_USERS:
            self.stdout.write(f"  - {user['username']:<12} contrasena: {user['password']}")

    # -- pasos --------------------------------------------------------------
    def _seed_users(self) -> None:
        repository = UserRepository()
        for spec in DEMO_USERS:
            try:
                repository.create(
                    spec["username"],
                    spec["password"],
                    display_name=spec["display_name"],
                    role=spec["role"],
                )
                self.stdout.write(self.style.SUCCESS(f"[OK]    usuario {spec['username']}"))
            except AccountsError as exc:
                self.stdout.write(self.style.WARNING(f"[AVISO] {exc}"))

    def _seed_players(self) -> None:
        repository = PlayerRepository()
        for spec in DEMO_PLAYERS:
            repository.create(spec["name"], spec["team"])
            self.stdout.write(self.style.SUCCESS(f"[OK]    jugador {spec['name']} ({spec['team']})"))

    def _seed_events(self) -> None:
        recorder = EventRecorder()
        repository = EventRepository()
        for kind, detail, severity in DEMO_EVENTS:
            recorder.record(
                kind,
                detail,
                actor="admin",
                severity=severity,
                source="esp32" if kind.startswith("sensor") else "web",
                match_id="M-DEMO-001",
            )
        total = repository.count()
        self.stdout.write(self.style.SUCCESS(f"[OK]    eventos sembrados (total en el nodo: {total})"))
        self.stdout.write(f"[INFO]  marca de tiempo: {timezone.now().isoformat(timespec='seconds')}")
