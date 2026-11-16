"""Servicios de infraestructura compartidos entre bloques."""

from .firebase import FirebaseError, FirebaseRealtimeDB, get_client

__all__ = ["FirebaseError", "FirebaseRealtimeDB", "get_client"]
