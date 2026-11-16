# PAINTBALL VR & IOT

Plataforma web de control para el proyecto academico
**"Modelo de realidad virtual e IoT para la simulacion interactiva de paintball
en entornos controlados"**.

Centro de control construido con **Django** siguiendo una arquitectura **MVI
(Model - View - Intent)** y organizado por **bloques funcionales**. La
autenticacion y el estado de dominio viven en **Firebase Realtime Database**.
La interfaz usa el tema **Tokyo Night / Omarchy OS** (tiling window manager).

---

## 1. Requisitos

- Python 3.13 o superior (probado con 3.14.2)
- Acceso a internet (Firebase Realtime Database)
- Firebase Realtime Database accesible con las reglas de lectura/escritura
  necesarias para el nodo raiz del proyecto

## 2. Instalacion

```powershell
cd C:\Users\USUARIO\OneDrive\Documents\VRT

# 1) Entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Dependencias
pip install -r requirements.txt

# 3) Configuracion de entorno
Copy-Item .env.example .env
#   Edita .env si necesitas cambiar la URL o el token de Firebase.

# 4) Infraestructura Django (sesiones y mensajes)
python manage.py migrate

# 5) Verificar la conexion con Firebase
python manage.py firebase_check

# 6) Sembrar datos de demostracion (usuarios, roster y eventos)
python manage.py seed_demo
```

## 3. Ejecucion

```powershell
python manage.py runserver 127.0.0.1:8765
```

Abre `http://127.0.0.1:8765/`. La raiz redirige al login.

### Credenciales de demostracion

| Usuario     | Contrasena  | Rol        |
|-------------|-------------|------------|
| `admin`     | `admin1234` | admin      |
| `jugador01` | `1234`      | operator   |
| `jugador02` | `1234`      | operator   |

Tambien puedes crear cuentas nuevas desde **Crear cuenta**: se registran en el
nodo `users` de Realtime Database.

---

## 4. Arquitectura MVI

Flujo unidireccional aplicado en **cada bloque**:

```
Intent  --dispatch-->  Reducer (puro)  -->  State + Effects
                                              |
                                              v
                                        Effect handlers (IO)
                                              |
                                  Intent de realimentacion
                                              |
                                              v
                                           Reducer ...
```

- **Intent**: describe *que* quiere hacer el usuario. Solo datos, inmutable.
- **Reducer**: funcion pura `(State, Intent) -> (State, [Effect])`. No toca red,
  sesion ni base de datos.
- **Effect**: efecto secundario *declarativo*. El reducer lo emite; un manejador
  registrado en el `Store` lo ejecuta.
- **Store**: ejecuta el ciclo completo (incluida la realimentacion) con un
  limite de iteraciones (`max_dispatches=64`) para detectar bucles.

La IO vive exclusivamente en los `handlers.py` de cada bloque, que pueden
devolver nuevos `Intent` para cerrar el ciclo.

En el servidor: **la vista es el despachador de intents**, **la plantilla es la
View**, y **la sesion / Firebase es la persistencia**.

---

## 5. Estructura de carpetas (por bloques)

```
VRT/
├── manage.py
├── requirements.txt
├── .env / .env.example
├── config/                       # Proyecto Django
│   ├── settings.py               # Apps, middleware, Firebase, TZ America/La_Paz
│   ├── urls.py                   # Enrutado raiz -> incluye cada bloque
│   ├── wsgi.py
│   └── asgi.py
│
├── core/                         # Nucleo MVI reutilizable + infraestructura
│   ├── mvi/
│   │   ├── intent.py             # Intent
│   │   ├── effect.py             # Effect
│   │   ├── state.py              # State (+ evolve)
│   │   ├── reducer.py            # Reducer
│   │   └── store.py              # Store (bucle de realimentacion)
│   ├── actor.py                  # Actor autenticado (inmutable)
│   ├── http/                     # Middleware, login_required, page_context
│   ├── services/firebase.py      # Cliente REST de Realtime Database
│   └── management/commands/      # firebase_check, seed_demo
│
├── theme/                        # BLOQUE DE TEMA Y ESTILOS (Tokyo Night)
│   ├── static/theme/css/
│   │   ├── tokens.css            # Paleta oficial + tokens de diseno
│   │   ├── reset.css
│   │   ├── layout.css            # topbar / sidebar / workspace / statusline
│   │   └── components.css        # paneles, botones, tablas, medidores, login
│   ├── templates/theme/          # base.html, auth_base.html, partials
│   ├── templatetags/ui.py        # {% icon %}, severity_class, percent, ascii_state
│   └── navigation.py             # Navegacion global del workspace
│
└── blocks/                       # Bloques funcionales
    ├── accounts/                 # Autenticacion contra el nodo users
    │   ├── mvi/                  # state, intents, effects, reducer, handlers, store
    │   ├── repositories/users.py # UserRepository (PBKDF2)
    │   ├── templates/blocks/accounts/
    │   └── views.py / urls.py
    ├── telemetry/                # Dominio compartido de eventos
    │   ├── models.py             # EventRecord
    │   ├── repositories/events.py# EventRepository (nodo events)
    │   └── services/recorder.py  # EventRecorder
    ├── dashboard/                # Panel principal (resumen consolidado)
    ├── simulation/               # Maquina de estados de la partida
    ├── players/                  # Roster (nodo players)
    └── history/                  # Visor de telemetria con filtro
```

Cada bloque funcional sigue la misma forma:

```
blocks/<bloque>/
├── __init__.py
├── apps.py
├── models.py                 # Dominio inmutable (dataclasses frozen)
├── mvi/
│   ├── state.py              # @dataclass(frozen=True) State
│   ├── intents.py            # Intents del bloque
│   ├── effects.py            # Effects del bloque
│   ├── reducer.py            # Funcion pura
│   ├── handlers.py           # IO (Firebase, sesion, telemetria)
│   └── store.py              # create_<bloque>_store()
├── repositories/             # Acceso a Realtime Database
├── services/                 # Logica de dominio adicional
├── templates/blocks/<bloque>/
│   ├── index.html            # Pagina completa (extends theme/base.html)
│   └── partials/
│       ├── <bloque>_view.html# Envoltorio con cabecera (objetivo de HTMX)
│       └── <panel>.html      # Panel interno
├── urls.py
└── views.py                  # Intent dispatcher
```

---

## 6. Interfaz (tema Tokyo Night / Omarchy OS)

El bloque `theme` concentra todo el estilo. Reglas aplicadas:

- **Cero emojis.** Indicadores ASCII puros (`>`, `::`, `[x]`, `-`, `*`) e iconos
  SVG monocromaticos de trazo fino (`stroke-width: 1.5`).
- **Estetica tiling**: contenedores rectangulares (`border-radius` 0-4px),
  separadores de `1px solid`, `box-shadow: none`, jerarquia tipografica
  monoespaciada y alta densidad de informacion.
- **Paleta oficial Tokyo Night** en `theme/static/theme/css/tokens.css`
  (Night y Storm).
- Interacciones `:hover` / `:focus` instantaneas (sin transiciones lentas).

Estructura visual tipo gestor de ventanas: `topbar` (marca + sesion),
`sidebar` (modulos), `workspace` (contenido) y `statusline` (estado MVI, nodo
RTDB, usuario y hora).

### HTMX

Los paneles se actualizan con **HTMX** (`unpkg.com/htmx.org@2.0.4`) mediante
`hx-post` / `hx-get`. Cada bloque expone una constante `PARTIAL` que apunta a un
envoltorio `*_view.html` (cabecera + panel), de modo que al refrescar tambien se
actualizan las insignias de la cabecera.

Todos los formularios conservan `method="post" action="..."`, por lo que la
plataforma **funciona igual sin JavaScript** (recarga completa).

---

## 7. Esquema de Firebase Realtime Database

Base de datos: `https://alvin-59045-default-rtdb.firebaseio.com/`

```
users/<clave>
  username       "jugador01"
  display_name   "Jugador 01"
  role           "operator" | "admin"
  active         true
  password_hash  "pbkdf2_sha256$..."      # hash de Django, nunca texto plano
  created_at     "2026-01-01T10:00:00-04:00"
  last_login     "2026-01-02T18:22:10-04:00"

players/<pushKey>
  name           "Ana Quispe"
  team           "azul" | "rojo" | "verde" | "amarillo"
  status         "activo" | "inactivo"
  hits           0
  shots          0
  created_at     "..."

sessions/<match_id>
  active, hp, max_hp, ammo, max_ammo, score, shots, hits
  match_id, started_at, finished_at
  actor, updated_at

events/<pushKey>
  kind           "partida:inicio" | "disparo" | "impacto" | "roster:alta" | ...
  detail         "Disparo detectado. Municion restante: 29."
  actor          "jugador01"
  severity       "info" | "success" | "warning" | "critical"
  source         "web" | "godot" | "esp32" | "mqtt" | "sistema"
  match_id       "M-20260101-120000"
  created_at     "2026-01-01T12:00:00-04:00"
```

### Seguridad (academico)

El login se valida **contra el nodo `users`**, no contra Firebase
Authentication. Las contrasenas se guardan como **hash PBKDF2-SHA256**
(`make_password` / `check_password`), nunca en claro. Para un entorno real se
recomienda Firebase Auth o reglas cerradas con token (`FIREBASE_DB_SECRET`).

---

## 8. Comandos de gestion

```powershell
# Diagnostico de conexion y conteo de nodos
python manage.py firebase_check

# Sembrar datos de demostracion
python manage.py seed_demo

# Solo eventos, o vaciar players/events antes de sembrar
python manage.py seed_demo --events-only
python manage.py seed_demo --reset
```

---

## 9. Integracion prevista (VR + IoT)

Esta version genera los eventos desde la propia plataforma (fuente `web`). La
integracion fisica se conecta escribiendo en el **mismo nodo `events`**:

- **Godot** (entorno VR) -> `source: "godot"`
- **ESP32 / sensores** -> `source: "esp32"`
- **MQTT** -> `source: "mqtt"`

Cualquier componente que haga `POST` a
`https://alvin-59045-default-rtdb.firebaseio.com/events.json` con el esquema de
`events/<pushKey>` aparecera automaticamente en el historial y el panel.

---

## 10. Modulos y rutas

| Bloque      | Ruta              | Descripcion                                   |
|-------------|-------------------|-----------------------------------------------|
| accounts    | `/cuenta/`        | Login, registro y cierre de sesion            |
| dashboard   | `/`               | Panel principal y `/proyecto/` (documentacion)|
| simulation  | `/simulacion/`    | Maquina de estados de la partida              |
| players     | `/jugadores/`     | Roster de participantes                       |
| history     | `/historial/`     | Telemetria de eventos con filtro              |

---

## 11. Documentacion ampliada

La carpeta `documentacion/` reune la documentacion tecnica completa en archivos
Markdown. Empieza por su indice:

- [`documentacion/README.md`](documentacion/README.md)

Contenido: vision general y stack, arquitectura MVI, estructura de carpetas,
bloques y modulos, mapa de conexiones entre modulos, modelo de datos de
Realtime Database, tema y frontend, instalacion y lanzamiento, referencia de
rutas, comandos, integracion VR/IoT y glosario.
#   v r t - r e p o s i t o r i o  
 