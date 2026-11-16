"""Servicios de dominio del bloque de telemetria."""

from .recorder import EventRecorder, record_event

__all__ = ["EventRecorder", "record_event"]
