"""Effect: describe *que* hay que hacer fuera del reducer. Solo datos."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Effect:
    """Efecto secundario declarativo (IO, persistencia, sesion, ...).

    El reducer nunca ejecuta un Effect: lo emite. Un manejador registrado en
    el Store lo interpreta y puede devolver nuevos Intent de realimentacion.

    Nota: esta clase no declara atributos de clase para no colisionar con los
    campos de las subclases.
    """

    def __str__(self) -> str:  # pragma: no cover - ayuda de depuracion
        return type(self).__name__


def effect_name(effect: Effect) -> str:
    """Nombre legible de un efecto (para registros y depuracion)."""
    return type(effect).__name__
