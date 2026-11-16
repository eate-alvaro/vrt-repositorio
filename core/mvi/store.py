"""
Store: runtime MVI.

Concentra el bucle unidireccional:

    1. recibe un Intent,
    2. aplica el reducer puro para obtener (estado nuevo, efectos),
    3. ejecuta cada efecto con su manejador registrado,
    4. encola los Intent de realimentacion devueltos por los manejadores.

Todo el ciclo se ejecuta dentro de un limite de iteraciones para detectar
bucles infinitos entre reducer y efectos.
"""

from __future__ import annotations

from collections import deque
from typing import Callable, Deque, Dict, Generic, Iterable, Optional, Type, TypeVar, Union

from .effect import Effect
from .intent import Intent
from .reducer import Reducer
from .state import State

StateT = TypeVar("StateT", bound=State)

# Un manejador ejecuta un efecto y puede devolver Intent de realimentacion.
EffectHandler = Callable[["Store", Effect], Union[None, Intent, Iterable[Intent]]]


class Store(Generic[StateT]):
    """Estado unico + reducer puro + manejadores de efectos."""

    def __init__(
        self,
        state: StateT,
        reducer: Reducer[StateT],
        handlers: Optional[Dict[Type[Effect], EffectHandler]] = None,
        *,
        max_dispatches: int = 64,
    ) -> None:
        self._state: StateT = state
        self._reducer = reducer
        self._handlers: Dict[Type[Effect], EffectHandler] = dict(handlers or {})
        self._max_dispatches = max_dispatches
        self._history: list[Intent] = []
        self._effects_log: list[Effect] = []

    # -- lectura ------------------------------------------------------------
    @property
    def state(self) -> StateT:
        return self._state

    @property
    def history(self) -> tuple[Intent, ...]:
        """Intents procesados, en orden (util para depuracion y auditoria)."""
        return tuple(self._history)

    @property
    def effects_log(self) -> tuple[Effect, ...]:
        return tuple(self._effects_log)

    # -- registro -----------------------------------------------------------
    def register(self, effect_type: Type[Effect], handler: EffectHandler) -> "Store[StateT]":
        self._handlers[effect_type] = handler
        return self

    # -- ciclo MVI ----------------------------------------------------------
    def dispatch(self, intent: Intent) -> StateT:
        """Procesa un intent y todo su arbol de realimentacion."""
        queue: Deque[Intent] = deque([intent])
        processed = 0

        while queue:
            current = queue.popleft()
            processed += 1
            if processed > self._max_dispatches:
                raise RuntimeError(
                    "Se detecto un bucle de intenciones en el Store MVI "
                    f"(mas de {self._max_dispatches} iteraciones)."
                )

            self._history.append(current)
            self._state, effects = self._reducer(self._state, current)

            for effect in effects or ():
                self._effects_log.append(effect)
                handler = self._handlers.get(type(effect))
                if handler is None:
                    continue
                feedback = handler(self, effect)
                if feedback is None:
                    continue
                if isinstance(feedback, Intent):
                    queue.append(feedback)
                else:
                    queue.extend(feedback)

        return self._state


def create_store(
    state: StateT,
    reducer: Reducer[StateT],
    handlers: Optional[Dict[Type[Effect], EffectHandler]] = None,
) -> Store[StateT]:
    """Fabrica de conveniencia para construir un Store."""
    return Store(state, reducer, handlers)
