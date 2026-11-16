"""
Configuracion central del proyecto Paintball VR & IoT.

Proyecto
--------
"Modelo de Realidad Virtual e IoT para la simulacion interactiva de Paintball
en entornos controlados".

Arquitectura
------------
MVI (Model - View - Intent) organizada por bloques funcionales:

    core/        nucleo MVI reutilizable (Store, Reducer, Intent, Effect)
    theme/       bloque de tema y estilos (Tokyo Night / Omarchy OS)
    blocks/      bloques funcionales (accounts, telemetry, dashboard, ...)
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Rutas base
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def env_bool(name: str, default: bool = False) -> bool:
    raw = env(name, "1" if default else "0").lower()
    return raw in {"1", "true", "yes", "on", "si", "sí"}


def env_int(name: str, default: int) -> int:
    try:
        return int(env(name, str(default)))
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    try:
        return float(env(name, str(default)))
    except ValueError:
        return default


def env_list(name: str, default: str = "") -> list[str]:
    raw = env(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Seguridad
# ---------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-insecure-change-me-in-production")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")

# ---------------------------------------------------------------------------
# Aplicaciones
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.sessions",
    "django.contrib.messages",
    # --- Nucleo MVI ---------------------------------------------------------
    "core",
    # --- Bloque de tema / estilos ------------------------------------------
    "theme",
    # --- Bloques funcionales ------------------------------------------------
    "blocks.accounts",
    "blocks.telemetry",
    "blocks.dashboard",
    "blocks.simulation",
    "blocks.players",
    "blocks.history",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Expone el actor autenticado en request.actor (soporte MVI).
    "core.http.middleware.ActorMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.app_context",
                "theme.context_processors.theme_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Base de datos (solo infraestructura Django: sesiones y mensajes)
# El estado de dominio vive en Firebase Realtime Database.
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Sesiones
# ---------------------------------------------------------------------------
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_NAME = "vrt_session"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 8
SESSION_SAVE_EVERY_REQUEST = True

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# ---------------------------------------------------------------------------
# Internacionalizacion
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "es"
TIME_ZONE = "America/La_Paz"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Archivos estaticos
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [p for p in [BASE_DIR / "static"] if p.exists()]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# ---------------------------------------------------------------------------
# Firebase Realtime Database
# ---------------------------------------------------------------------------
FIREBASE_DB_URL = env("FIREBASE_DB_URL", "https://alvin-59045-default-rtdb.firebaseio.com/")
FIREBASE_DB_SECRET = env("FIREBASE_DB_SECRET", "")
FIREBASE_TIMEOUT = env_float("FIREBASE_TIMEOUT", 8.0)
FIREBASE_USERS_NODE = env("FIREBASE_USERS_NODE", "users")

# ---------------------------------------------------------------------------
# Identidad de la aplicacion
# ---------------------------------------------------------------------------
VRT_APP_NAME = env("VRT_APP_NAME", "PAINTBALL VR & IOT")
VRT_APP_TAGLINE = env("VRT_APP_TAGLINE", "PLATAFORMA DE SIMULACION")
VRT_APP_VERSION = env("VRT_APP_VERSION", "1.0.0")
VRT_DEMO_MODE = env_bool("VRT_DEMO_MODE", False)

# ---------------------------------------------------------------------------
# Registro de eventos
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "vrt": {
            "format": "[{asctime}] {levelname:<7} {name}: {message}",
            "style": "{",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "vrt"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "vrt": {"handlers": ["console"], "level": "DEBUG" if DEBUG else "INFO", "propagate": False},
    },
}
