"""Intent: describe *que* quiere hacer el usuario. No contiene logica."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Intent:
    """Unidad de intencion (usuario, sistema o realimentacion de efectos).

    Los Intent son inmutables y solo transportan datos. Cada bloque declara
    sus propios Intent heredando de esta clase.

    Nota: esta clase no declara atributos de clase para no colisionar con los
    campos de las subclases (los `dataclass` heredan el atributo como valor
    por defecto).
    """

    def __str__(self) -> str:  # pragma: no cover - ayuda de depuracion
        return type(self).__name__


def intent_name(intent: Intent) -> str:
    """Nombre legible de un intent (para registros y depuracion)."""
    return type(intent).__name__
