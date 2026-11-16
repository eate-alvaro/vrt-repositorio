# 02 - ARQUITECTURA MVI

El proyecto implementa **MVI (Model - View - Intent)**: un patron de flujo
**unidireccional** en el que el estado solo cambia por la aplicacion de
funciones puras sobre intenciones.

## 2.1 Idea central

```
   Usuario
      |
      |  (1) emite una Intencion
      v
   Intent  ------>  Reducer (funcion PURA)  ------>  (State nuevo, [Effects])
                                                              |
                                                              |  (2) el Store
                                                              v      ejecuta
                                                        Effect handler (IO)
                                                              |
                                                              |  (3) puede emitir
                                                              v      una Intencion
                                                        Intent de realimentacion
                                                              |
                                                              v
                                                           Reducer ...  (vuelve a 1)
```

Reglas:

1. El **Reducer** es puro: `(State, Intent) -> (State, [Effect])`. Nunca toca
   red, sesion ni base de datos.
2. Los **Effects** son *datos declarativos*. El reducer los emite, no los
   ejecuta.
3. Los **handlers** ejecutan la IO y pueden devolver un `Intent` de
   realimentacion, cerrando el ciclo.
4. El **Store** orquesta todo el bucle.

## 2.2 Piezas del nucleo (`core/mvi/`)

| Archivo | Clase / funcion | Responsabilidad |
|---------|-----------------|-----------------|
| `intent.py` | `Intent` | Base inmutable de toda intencion |
| `effect.py` | `Effect` | Base inmutable de todo efecto declarativo |
| `state.py` | `State` (+ `evolve`) | Base inmutable del estado; `evolve(**cambios)` devuelve una copia |
| `reducer.py` | `Reducer`, `no_change` | Contrato `(State, Intent) -> (State, [Effect])` |
| `store.py` | `Store`, `create_store` | Runtime: ejecuta el ciclo completo con realimentacion |

### Detalle de `Store.dispatch`

`Store.dispatch(intent)` mantiene una **cola** de intents. Mientras haya
intents:

1. Aplica el reducer y obtiene `(estado_nuevo, efectos)`.
2. Ejecuta cada efecto con su handler registrado.
3. Encola los intents que devuelva el handler.

Todo el ciclo esta acotado por `max_dispatches=64`: si se supera, lanza
`RuntimeError` para detectar bucles infinitos entre reducer y efectos.

Tambien expone `history` (intents procesados) y `effects_log` (efectos
ejecutados), utiles para depuracion y auditoria.

## 2.3 Traduccion del MVI al servidor Django

No existe un store en el navegador. El patron se aplica **en el servidor**:

| Concepto MVI | En este proyecto |
|--------------|------------------|
| **Intent** | El cuerpo de una peticion HTTP (POST/GET) traducido a una dataclass |
| **Model / State** | La dataclass de estado del bloque + su persistencia |
| **View** | La plantilla Django que renderiza el estado |
| **Reducer** | `reduce_<bloque>(state, intent)` en `mvi/reducer.py` |
| **Effect + handler** | `mvi/effects.py` + `mvi/handlers.py` (IO real) |
| **Store** | `create_<bloque>_store()` en `mvi/store.py` |
| **Persistencia** | Sesion de Django (`request.session`) y/o Firebase RTDB |

Por tanto:

- La **vista es el despachador de intents**: recibe la peticion, construye el
  Store, despacha y renderiza.
- La **plantilla es la View**: solo lee el estado, no calcula negocio.
- La **sesion / Firebase es el Model persistido**.

## 2.4 Estructura interna de un bloque MVI

Cada bloque funcional que usa MVI tiene esta forma:

```
blocks/<bloque>/
├── mvi/
│   ├── context.py    # Dependencias inyectadas (repositorios, request, etc.)
│   ├── state.py      # @dataclass(frozen=True) <Bloque>State(State)
│   ├── intents.py    # Intents del bloque
│   ├── effects.py    # Effects del bloque
│   ├── reducer.py    # Funcion pura reduce_<bloque>
│   ├── handlers.py   # IO: implementa cada Effect
│   └── store.py      # create_<bloque>_store()
├── repositories/     # Acceso a Realtime Database
├── services/         # Logica de dominio adicional
├── templates/...      # View (plantillas)
├── urls.py           # Rutas (namespace del bloque)
└── views.py          # Intent dispatcher
```

## 2.5 Ejemplo completo: registrar un disparo

Bloque `simulation`. El usuario pulsa "disparar".

**1) La vista traduce la accion a un Intent** (`blocks/simulation/views.py`):

```python
if action == "shoot":
    return Shoot()
```

**2) El reducer decide el estado nuevo y los efectos** (`mvi/reducer.py`):

```python
if isinstance(intent, Shoot):
    if not state.active:
        return _feedback(state, "aviso", "Primero inicia la partida."), ()
    if state.ammo <= 0:
        return _feedback(state, "aviso", "No queda municion en el marcador."), ()
    updated = state.evolve(
        ammo=state.ammo - 1,
        shots=state.shots + 1,
        score=state.score + 10,
        last_kind="disparo",
        last_detail=f"Disparo detectado. Municion restante: {state.ammo - 1}.",
    )
    return updated, (
        PersistMatch(snapshot=updated),
        RecordMatchEvent(kind="disparo", detail=updated.last_detail, ...),
    )
```

**3) Los handlers ejecutan la IO** (`mvi/handlers.py`):

- `PersistMatch` guarda el estado en la sesion y espeja en el nodo `sessions`.
- `RecordMatchEvent` escribe un evento en el nodo `events`.

**4) El Store cierra el ciclo**: si un handler devolviera un Intent, se volveria
a aplicar el reducer. En este caso no hay realimentacion.

**5) La plantilla renderiza** el estado resultante (municion 29, puntuacion 10).

## 2.6 Realimentacion (feedback loop)

Es el mecanismo que cierra el ciclo. Ejemplos reales en el proyecto:

- **accounts**: `SubmitLogin` -> `VerifyCredentials` -> (handler consulta
  Firebase) -> `AuthenticationSucceeded` / `AuthenticationFailed` -> reducer
  actualiza el estado y emite `OpenSession` + `RecordLogin`.
- **players**: `AddPlayer` -> `PersistPlayer` -> (handler escribe) ->
  `LoadRoster` -> `FetchPlayers` -> `RosterLoaded` -> estado con el roster
  actualizado. Asi, tras cualquier alta/baja/cambio se relee el roster real.
- **history**: `ClearHistory` -> `PurgeEvents` -> `LoadHistory` -> `FetchEvents`
  -> `HistoryLoaded`.

## 2.7 Inmutabilidad

- `State`, `Intent` y `Effect` heredan de `@dataclass(frozen=True)`.
- `State.evolve(**cambios)` (basado en `dataclasses.replace`) devuelve una copia
  nueva; nunca se muta el estado en sitio.
- Los repositorios convierten los diccionarios JSON de Firebase en dataclasses
  inmutables (`PlayerRecord`, `EventRecord`, `UserRecord`).

## 2.8 Reglas de oro (para contribuir)

1. **No poner IO en el reducer.** Si necesitas red o disco, crea un `Effect` y
   su handler.
2. **No mutar el estado.** Usa `state.evolve(...)`.
3. **Los handlers devuelven intents**, no estados.
4. **La vista solo despacha y renderiza**; no contiene reglas de negocio.
5. **Cada bloque es autonomo**: solo depende del nucleo `core` y, como mucho,
   del bloque de dominio compartido `telemetry`.
