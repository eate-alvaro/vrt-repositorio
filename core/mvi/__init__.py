"""
Nucleo MVI (Model - View - Intent).

Flujo unidireccional:

    Intent  --dispatch-->  Reducer (puro)  -->  State + Effects
                                                  |
                                                  v
                                            Effect handlers (IO)
                                                  |
                                        Intent de realimentacion
                                                  |
                                                  v
                                               Reducer ...

Los reducers son funciones puras: nunca realizan efectos secundarios.
Los efectos son *datos* declarativos que un manejador ejecuta fuera del
reducer, lo que hace el estado predecible y verificable.
"""

from __future__ import annotations

from .effect import Effect
from .intent import Intent
from .reducer import Reducer, no_change
from .state import State
from .store import EffectHandler, Store, create_store

__all__ = [
    "Effect",
    "Intent",
    "Reducer",
    "State",
    "Store",
    "EffectHandler",
    "create_store",
    "no_change",
]
