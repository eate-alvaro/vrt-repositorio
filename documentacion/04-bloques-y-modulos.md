# 04 - BLOQUES Y MODULOS

El proyecto se divide en **bloques funcionales**. Cada bloque es una app Django
independiente con su propio namespace de URLs, su ciclo MVI (si tiene
interaccion) y sus repositorios de datos.

Un bloque puede ser de tres tipos:

- **Nucleo** (`core`): infraestructura reutilizable, sin conocer los bloques.
- **Tema** (`theme`): presentacion y estilo global.
- **Funcional** (`blocks/*`): una capacidad concreta del sistema.
- **Dominio compartido** (`blocks/telemetry`): modelo y acceso a datos que
  varios bloques consumen.

---

## 4.1 `core` - Nucleo MVI e infraestructura

No es un bloque funcional: es la base que todos comparten.

| Pieza | Archivo | Que aporta |
|-------|---------|------------|
| Nucleo MVI | `core/mvi/` | `Intent`, `Effect`, `State`, `Reducer`, `Store` |
| Actor | `core/actor.py` | Identidad autenticada inmutable (usuario, nombre, rol, iniciales) |
| Middleware | `core/http/middleware.py` | `ActorMiddleware`: expone `request.actor` leyendo la sesion |
| Decoradores | `core/http/decorators.py` | `login_required`, `safe_redirect_target`, `wants_partial` |
| Contexto | `core/http/context.py` | `page_context()` para las vistas |
| Cliente Firebase | `core/services/firebase.py` | `FirebaseRealtimeDB` (GET/PUT/PATCH/POST/DELETE/keys/health) |
| Contexto global | `core/context_processors.py` | `app_context`: actor, hora local, host de Firebase |
| Comandos | `core/management/commands/` | `firebase_check`, `seed_demo` |

---

## 4.2 `theme` - Bloque de tema y estilos

Concentra **todo** el estilo y la presentacion. Ver
[07-tema-y-frontend.md](07-tema-y-frontend.md).

| Pieza | Archivo | Que aporta |
|-------|---------|------------|
| Tokens | `static/theme/css/tokens.css` | Paleta Tokyo Night y variables de diseno |
| Reset | `static/theme/css/reset.css` | Normalizacion base |
| Layout | `static/theme/css/layout.css` | Estructura tipo tiling WM |
| Componentes | `static/theme/css/components.css` | Paneles, botones, tablas, medidores, login |
| Layout app | `templates/theme/base.html` | topbar + sidebar + workspace + statusline |
| Layout acceso | `templates/theme/auth_base.html` | Pantalla de login/registro |
| Navegacion | `navigation.py` | Entradas del sidebar |
| Etiquetas | `templatetags/ui.py` | `{% icon %}`, `severity_class`, `percent`, `ascii_state` |
| Contexto | `context_processors.py` | `theme_context`: nombre de app, tema, navegacion |

---

## 4.3 `blocks/accounts` - Autenticacion

**Proposito**: login, registro y cierre de sesion contra el nodo `users`.

| Aspecto | Detalle |
|---------|---------|
| Rutas | `/cuenta/entrar/`, `/cuenta/registro/`, `/cuenta/salir/` |
| Namespace | `accounts` |
| Persistencia | Nodo `users` (Firebase) + sesion de Django |
| Repositorio | `UserRepository` (hash PBKDF2-SHA256 con `make_password`/`check_password`) |

**MVI**

| Elemento | Valores |
|----------|---------|
| State | `AuthState(mode, status, actor, username, error, attempts, ...)` |
| Intents | `SubmitLogin`, `SubmitRegistration`, `RequestLogout`, `AuthenticationSucceeded`, `AuthenticationFailed` |
| Effects | `VerifyCredentials`, `CreateAccount`, `OpenSession`, `CloseSession`, `RecordLogin` |
| Reducer | `reduce_auth` |

**Flujo de realimentacion**

```
SubmitLogin -> VerifyCredentials -> (consulta users)
            -> AuthenticationSucceeded -> OpenSession + RecordLogin
            |  o AuthenticationFailed -> estado de error
```

---

## 4.4 `blocks/telemetry` - Dominio compartido de eventos

**Proposito**: modelo y escritura homogenea de telemetria. Es el **unico bloque
del que dependen los demas**.

| Pieza | Archivo | Que aporta |
|-------|---------|------------|
| Modelo | `models.py` | `EventRecord` (kind, detail, actor, severity, source, match_id) |
| Repositorio | `repositories/events.py` | `EventRepository` (nodo `events`) |
| Servicio | `services/recorder.py` | `EventRecorder.record(...)` (mejor esfuerzo) |

Constantes del dominio:

- `SEVERITIES = ("info", "success", "warning", "critical")`
- `SOURCES = ("web", "godot", "esp32", "mqtt", "sistema")`

No tiene MVI propio porque no tiene interfaz: es una capacidad de servicio.

---

## 4.5 `blocks/dashboard` - Panel principal

**Proposito**: consolidar el estado del sistema (jugadores, eventos, partidas,
conexion) en una sola fotografia tolerante a fallos.

| Aspecto | Detalle |
|---------|---------|
| Rutas | `/` (index), `/proyecto/` (about) |
| Namespace | `dashboard` |
| Servicio | `DashboardService.snapshot()` |
| Lee de | `players` + `events` + `sessions` + `health()` |

**MVI**

| Elemento | Valores |
|----------|---------|
| State | `DashboardState(status, players, events, sessions_count, events_count, online, degraded)` |
| Intents | `LoadDashboard`, `RefreshDashboard`, `DashboardLoaded`, `DashboardFailed` |
| Effects | `FetchDashboardSnapshot` |
| Reducer | `reduce_dashboard` |

---

## 4.6 `blocks/simulation` - Maquina de estados de la partida

**Proposito**: dirigir la partida (iniciar, disparar, recibir impacto,
finalizar, reiniciar) y emitir telemetria.

| Aspecto | Detalle |
|---------|---------|
| Rutas | `/simulacion/` (index), `/simulacion/accion/` (action) |
| Namespace | `simulation` |
| Persistencia | Sesion (autoritativa) + nodo `sessions` (espejo) |
| Repositorios | `SessionRepository` (nodo `sessions`) |
| Servicios | `load_match` / `save_match` / `clear_match` (sesion) |

**MVI**

| Elemento | Valores |
|----------|---------|
| State | `MatchState(active, hp, ammo, score, shots, hits, match_id, last_*)` |
| Intents | `StartMatch`, `Shoot`, `RegisterHit`, `FinishMatch`, `ResetMatch` |
| Effects | `PersistMatch`, `RecordMatchEvent` |
| Reducer | `reduce_match` |

Reglas de la partida (en el reducer, constantes en `state.py`):

- Vida maxima `MAX_HP = 100`, dano por impacto `HIT_DAMAGE = 20`.
- Municion maxima `MAX_AMMO = 30`.
- Cada disparo resta 1 de municion y suma 10 de puntuacion.
- Si la vida llega a 0, el jugador queda **eliminado** (partida inactiva).

---

## 4.7 `blocks/players` - Roster

**Proposito**: administrar los participantes del nodo `players`.

| Aspecto | Detalle |
|---------|---------|
| Rutas | `/jugadores/`, `/jugadores/agregar/`, `/jugadores/<id>/estado/`, `/jugadores/<id>/eliminar/` |
| Namespace | `players` |
| Repositorio | `PlayerRepository` (nodo `players`) |
| Modelo | `PlayerRecord` (name, team, status, hits, shots) |

**MVI**

| Elemento | Valores |
|----------|---------|
| State | `RosterState(players, status, error, form_name, form_team)` |
| Intents | `LoadRoster`, `AddPlayer`, `RemovePlayer`, `TogglePlayer`, `RosterLoaded`, `RosterFailed` |
| Effects | `FetchPlayers`, `PersistPlayer`, `DeletePlayer`, `UpdatePlayerStatus`, `LogRosterEvent` |
| Reducer | `reduce_roster` |

**Detalle importante**: la vista usa `_store_with_roster(request)` para
**precargar el roster** antes de despachar `AddPlayer` / `TogglePlayer` /
`RemovePlayer`. Sin esa precarga, el reducer no encontraria el jugador objetivo
(ese fue el bug de "Jugador no encontrado").

Equipos validos: `azul`, `rojo`, `verde`, `amarillo`. Estados: `activo`,
`inactivo`.

---

## 4.8 `blocks/history` - Historial de telemetria

**Proposito**: leer y filtrar los eventos del nodo `events`.

| Aspecto | Detalle |
|---------|---------|
| Rutas | `/historial/` (index), `/historial/vaciar/` (clear) |
| Namespace | `history` |
| Repositorio | `EventRepository` (nodo `events`) |
| Limite por defecto | 200 eventos |

**MVI**

| Elemento | Valores |
|----------|---------|
| State | `HistoryState(events, severity_filter, status, limit)` |
| Intents | `LoadHistory`, `SetSeverityFilter`, `ClearHistory`, `HistoryLoaded`, `HistoryFailed` |
| Effects | `FetchEvents`, `PurgeEvents` |
| Reducer | `reduce_history` |

Filtros disponibles (`FILTERS`): `todos`, `info`, `success`, `warning`,
`critical`. El filtro se aplica en la **propiedad derivada**
`visible_events` del estado, no en el reducer.

---

## 4.9 Resumen de intents y effects por bloque

| Bloque | Intents | Effects |
|--------|---------|---------|
| accounts | 5 | 5 |
| dashboard | 4 | 1 |
| simulation | 5 | 2 |
| players | 6 | 5 |
| history | 5 | 2 |

(Telemetry no tiene MVI; aporta `EventRecorder`.)
