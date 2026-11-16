# 09 - REFERENCIA DE RUTAS

El enrutado raiz (`config/urls.py`) incluye un modulo de rutas por bloque, de
modo que la estructura de URLs refleja la arquitectura por bloques.

```python
urlpatterns = [
    path("", include("blocks.dashboard.urls")),
    path("cuenta/", include("blocks.accounts.urls")),
    path("simulacion/", include("blocks.simulation.urls")),
    path("jugadores/", include("blocks.players.urls")),
    path("historial/", include("blocks.history.urls")),
]
```

## 9.1 Tabla completa de rutas

| URL | Metodo | Namespace:name | Vista | Intent / accion |
|-----|--------|----------------|-------|-----------------|
| `/` | GET | `dashboard:index` | `dashboard.views.index` | `LoadDashboard` |
| `/proyecto/` | GET | `dashboard:about` | `dashboard.views.about` | (estatico) |
| `/cuenta/entrar/` | GET, POST | `accounts:login` | `accounts.views.login_view` | `SubmitLogin` |
| `/cuenta/registro/` | GET, POST | `accounts:register` | `accounts.views.register_view` | `SubmitRegistration` |
| `/cuenta/salir/` | POST | `accounts:logout` | `accounts.views.logout_view` | `RequestLogout` |
| `/simulacion/` | GET | `simulation:index` | `simulation.views.index` | (carga partida) |
| `/simulacion/accion/` | POST | `simulation:action` | `simulation.views.action` | `StartMatch` / `Shoot` / `RegisterHit` / `FinishMatch` / `ResetMatch` |
| `/jugadores/` | GET | `players:index` | `players.views.index` | `LoadRoster` |
| `/jugadores/agregar/` | POST | `players:add` | `players.views.add` | `AddPlayer` |
| `/jugadores/<id>/estado/` | POST | `players:toggle` | `players.views.toggle` | `TogglePlayer` |
| `/jugadores/<id>/eliminar/` | POST | `players:remove` | `players.views.remove` | `RemovePlayer` |
| `/historial/` | GET | `history:index` | `history.views.index` | `LoadHistory` + `SetSeverityFilter` |
| `/historial/vaciar/` | POST | `history:clear` | `history.views.clear` | `ClearHistory` |

## 9.2 Parametros y campos de formulario

### `/simulacion/accion/`

| Campo | Valores |
|-------|---------|
| `action` | `start` \| `shoot` \| `hit` \| `finish` \| `reset` |

Traduccion en `simulation/views.py::_build_intent`:

- `start` -> `StartMatch(match_id, started_at)`
- `shoot` -> `Shoot()`
- `hit` -> `RegisterHit(received_at)`
- `finish` -> `FinishMatch(finished_at)`
- `reset` -> `ResetMatch()`

### `/jugadores/agregar/`

| Campo | Valores |
|-------|---------|
| `name` | texto (obligatorio) |
| `team` | `azul` \| `rojo` \| `verde` \| `amarillo` |

### `/historial/` (GET)

| Parametro | Valores |
|-----------|---------|
| `severity` | `todos` \| `info` \| `success` \| `warning` \| `critical` |

### `/historial/vaciar/` (POST)

| Campo | Valores |
|-------|---------|
| `severity` | filtro que se conserva tras vaciar |

### `/cuenta/entrar/` (POST)

| Campo | Notas |
|-------|-------|
| `username` | obligatorio |
| `password` | obligatorio |
| `remember` | opcional (sesion extendida a 14 dias) |
| `next` | redireccion post-login validada |

### `/cuenta/registro/` (POST)

| Campo | Notas |
|-------|-------|
| `username` | obligatorio |
| `password` | obligatorio, minimo 4 caracteres |
| `display_name` | opcional |

## 9.3 Proteccion de acceso

- Todas las vistas de bloques usan el decorador `@login_required`
  (`core/http/decorators.py`), que redirige a `accounts:login` conservando el
  destino en `?next=`.
- El login/registro redirigen al panel si ya hay sesion activa.
- El cierre de sesion solo acepta `POST`.

## 9.4 Paginas de error

| Codigo | Plantilla |
|--------|-----------|
| 404 | `templates/404.html` |
| 500 | `templates/500.html` |

## 9.5 Respuestas parciales (HTMX)

Una misma vista devuelve la pagina completa o solo el envoltorio del bloque,
segun `wants_partial(request)`:

- `True` si la cabecera `HX-Request: true` o el parametro `?partial=1`.
- `True` -> plantilla `PARTIAL` (`*_view.html`).
- `False` -> plantilla `FULL` (`index.html`).
