# 05 - MAPA DE CONEXIONES

Este documento responde a: **que modulos estan conectados y como**. El proyecto
respeta una direccion de dependencias clara: los bloques funcionales dependen de
`core` y del dominio compartido `telemetry`, pero **nunca al reves**.

## 5.1 Grafo de dependencias (vision general)

```
                         +---------------------+
                         |        config       |  settings / urls
                         +----------+----------+
                                    |  incluye
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
   +---------+              +-------------+             +---------------+
   |  core   |<-------------|   theme     |             |   blocks/*    |
   | (MVI +  |              | (estilos y  |             |  (features)   |
   |  infra) |              |  plantillas)|             |               |
   +---------+              +-------------+             +-------+-------+
        ^                                                       |
        |                                                       | usa
        |  todos los bloques usan core                          v
        |                                            +---------------------+
        +--------------------------------------------|  blocks/telemetry   |
                                                     | (dominio compartido)|
                                                     +----------+----------+
                                                                ^
                                                                | eventos
                    +------------------+------------------+-----+-----+
                    |                  |                  |           |
              +-----+----+      +------+-----+      +------+-----+ +---+------+
              | players  |      | simulation |      |  history   | |dashboard |
              +----------+      +------------+      +------------+ +----+-----+
                                                                        |
                                          dashboard consolida a los tres -+
```

## 5.2 Dependencias por bloque

| Bloque | Depende de `core` | Depende de `theme` | Depende de otros bloques |
|--------|:-----------------:|:------------------:|--------------------------|
| `theme` | No | - | No |
| `accounts` | Si | Si (plantillas) | No |
| `telemetry` | Si (solo Firebase) | No | No |
| `players` | Si | Si | **telemetry** (recorder) |
| `simulation` | Si | Si | **telemetry** (recorder) |
| `history` | Si | Si | **telemetry** (model + repo) |
| `dashboard` | Si | Si | **players**, **simulation**, **telemetry** |

Reglas derivadas:

- **`core` no importa ningun bloque.** Es reutilizable y no conoce el dominio.
- **`theme` no importa ningun bloque funcional**; solo recibe datos por contexto.
- **`telemetry` es el hub de datos**: lo consumen players, simulation, history y
  dashboard.
- **`accounts` es independiente**: solo toca Firebase y la sesion.
- **`dashboard` es el unico agregador**: lee de tres bloques a la vez.

## 5.3 Flujo de una peticion (conexion HTTP -> MVI -> datos -> View)

Ejemplo: `POST /jugadores/agregar/`

```
 Navegador
    |
    |  POST /jugadores/agregar/  (name, team)   [HTMX o form normal]
    v
 config/urls.py
    |  "jugadores/" -> include("blocks.players.urls")
    v
 blocks/players/urls.py
    |  "agregar/" -> views.add
    v
 blocks/players/views.py  (INTENT DISPATCHER)
    |  construye RosterContext(PlayerRepository, EventRecorder)
    |  create_roster_store(...)  ->  Store
    |  store.dispatch(AddPlayer(name, team))
    v
 core/mvi/store.py  (Store)
    |
    +--> blocks/players/mvi/reducer.py  reduce_roster  (PURO)
    |        devuelve (estado_nuevo, [PersistPlayer, LogRosterEvent])
    |
    +--> blocks/players/mvi/handlers.py
             PersistPlayer -> PlayerRepository.create -> Firebase (nodo players)
             LogRosterEvent -> EventRecorder.record   -> Firebase (nodo events)
             (el handler devuelve LoadRoster)
    |
    +--> vuelve al reducer: LoadRoster -> FetchPlayers
             FetchPlayers -> PlayerRepository.list_all -> Firebase
             -> RosterLoaded(players) -> estado "ready"
    v
 blocks/players/views.py  _render(...)
    |  wants_partial(request) ? roster_view.html : index.html
    v
 theme/base.html  (View)  ->  HTML al navegador
```

## 5.4 Conexiones entre bloques en detalle

### dashboard -> players / simulation / telemetry

`blocks/dashboard/services/snapshot.py` importa:

```python
from blocks.players.models import PlayerRecord
from blocks.players.repositories.players import PlayerRepository
from blocks.simulation.repositories.sessions import SessionRepository
from blocks.telemetry.models import EventRecord
from blocks.telemetry.repositories.events import EventRepository
```

Es la unica conexion cruzada "amplia" del sistema, y es de **solo lectura**.

### players / simulation -> telemetry

Ambos importan el registrador de eventos:

```python
from blocks.telemetry.services.recorder import EventRecorder
```

Lo usan en sus handlers (`LogRosterEvent`, `RecordMatchEvent`) para escribir en
el nodo `events` sin conocer los detalles de Realtime Database.

### history -> telemetry

`blocks/history/mvi/handlers.py` importa el repositorio de eventos:

```python
from blocks.telemetry.repositories.events import EventRepository
```

## 5.5 Conexiones con el nucleo

Todos los bloques funcionales comparten estas importaciones de `core`:

| Importacion | Se usa para |
|-------------|-------------|
| `core.mvi` (`Intent`, `Effect`, `State`, `Store`, `create_store`) | Definir el ciclo MVI |
| `core.actor.Actor` | Identidad del usuario (accounts) |
| `core.http.decorators` | `login_required`, `wants_partial` |
| `core.http.context.page_context` | Contexto de plantilla |
| `core.services.firebase` | Cliente REST y `FirebaseError` |
| `core.http.middleware` | `write_actor` (accounts) |

## 5.6 Diagrama de estados del Store (ciclo de realimentacion)

```
        dispatch(Intent)
              |
              v
      +----------------+      efectos      +-------------------+
      |    Reducer     |------------------>|  Effect handlers  |
      |   (puro)       |                   |      (IO)         |
      +----------------+                   +---------+---------+
              ^                                      |
              |                                      | devuelve
              |  Intent de realimentacion            v
              +-------------------------------- Intent(es)
                         (encolados)
              |
        max_dispatches = 64  ->  guarda contra bucles
```

## 5.7 Persistencia: donde escribe cada bloque

| Bloque | Sesion Django | Nodo RTDB `users` | `players` | `sessions` | `events` |
|--------|:-------------:|:-----------------:|:---------:|:----------:|:--------:|
| accounts | escritura | lectura/escritura | - | - | - |
| players | - | - | lectura/escritura | - | escritura |
| simulation | lectura/escritura | - | - | escritura | escritura |
| history | - | - | - | - | lectura/borrado |
| dashboard | - | - | lectura | lectura | lectura |
