# 12 - GLOSARIO Y CONVENCIONES

## 12.1 Terminos de arquitectura

| Termino | Significado |
|---------|-------------|
| **MVI** | Model - View - Intent. Patron de flujo unidireccional. |
| **Intent** | Describe *que* quiere hacer el usuario. Solo datos, inmutable. |
| **State** | Estado inmutable de un bloque. |
| **Reducer** | Funcion pura `(State, Intent) -> (State, [Effect])`. |
| **Effect** | Efecto secundario declarativo (IO). Lo emite el reducer, no lo ejecuta. |
| **Handler** | Funcion que ejecuta un Effect (IO real). Puede devolver un Intent. |
| **Store** | Runtime MVI: ejecuta el ciclo completo con realimentacion. |
| **Realimentacion** | Intent que devuelve un handler para cerrar el ciclo. |
| **Reducer puro** | Sin efectos secundarios: mismo input -> mismo output. |
| **Bloque** | App Django autocontenida que implementa una capacidad. |
| **Namespace** | Prefijo de las rutas de un bloque (ej. `players:add`). |

## 12.2 Terminos del dominio

| Termino | Significado |
|---------|-------------|
| **Actor** | Usuario autenticado (inmutable): username, display_name, role. |
| **Roster** | Conjunto de jugadores registrados (nodo `players`). |
| **Partida / Match** | Sesion de juego con vida, municion y puntuacion. |
| **match_id** | Identificador de partida (ej. `M-20260101-120000`). |
| **Telemetria** | Conjunto de eventos registrados (nodo `events`). |
| **Severidad** | Nivel de un evento: info, success, warning, critical. |
| **Fuente** | Origen de un evento: web, godot, esp32, mqtt, sistema. |
| **RTDB** | Firebase Realtime Database. |
| **HTMX** | Libreria JS para actualizar paneles sin recargar la pagina. |

## 12.3 Constantes del sistema

| Constante | Valor | Ubicacion |
|-----------|-------|-----------|
| `MAX_HP` | 100 | `blocks/simulation/mvi/state.py` |
| `MAX_AMMO` | 30 | `blocks/simulation/mvi/state.py` |
| `HIT_DAMAGE` | 20 | `blocks/simulation/mvi/state.py` |
| `FILTERS` | todos, info, success, warning, critical | `blocks/history/mvi/state.py` |
| `TEAMS` | azul, rojo, verde, amarillo | `blocks/players/models.py` |
| `STATUSES` | activo, inactivo | `blocks/players/models.py` |
| `SEVERITIES` | info, success, warning, critical | `blocks/telemetry/models.py` |
| `SOURCES` | web, godot, esp32, mqtt, sistema | `blocks/telemetry/models.py` |
| `max_dispatches` | 64 | `core/mvi/store.py` |

## 12.4 Convenciones de codigo

1. **Idioma**: identificadores y textos en espanol; **sin tildes ni caracteres
   no ASCII** en el codigo.
2. **Inmutabilidad**: `@dataclass(frozen=True)` para State/Intent/Effect y para
   los modelos de dominio.
3. **Sin IO en el reducer**: la IO va en `handlers.py`.
4. **Sin emojis** en la interfaz: ASCII (`>`, `::`, `[x]`, `-`, `*`) o iconos SVG.
5. **Separacion de plantillas**: `*_view.html` (envoltorio, objetivo HTMX) +
   `*_panel.html` (panel interno).
6. **Un bloque = un namespace de URLs** declarado con `app_name`.

## 12.5 Siglas

| Sigla | Significado |
|-------|-------------|
| MVI | Model - View - Intent |
| RTDB | Realtime Database |
| CRUD | Create, Read, Update, Delete |
| CSRF | Cross-Site Request Forgery (proteccion de Django) |
| PBKDF2 | Algoritmo de derivacion de claves para hashear contrasenas |
| IoT | Internet of Things |
| VR | Virtual Reality |
| CDN | Content Delivery Network |
| WSGI / ASGI | Interfaces de servidor web de Python |

## 12.6 Donde buscar cada cosa

| Si quieres... | Ve a... |
|---------------|---------|
| Cambiar colores del tema | `theme/static/theme/css/tokens.css` |
| Cambiar la navegacion | `theme/navigation.py` |
| Anadir un icono | `theme/templatetags/ui.py` (`_ICONS`) |
| Cambiar reglas de la partida | `blocks/simulation/mvi/reducer.py` |
| Cambiar el esquema de datos | `blocks/*/models.py` y `repositories/` |
| Anadir una ruta | `blocks/<bloque>/urls.py` + `views.py` |
| Cambiar la configuracion | `config/settings.py` y `.env` |
| Documentar algo | Esta carpeta `documentacion/` |
