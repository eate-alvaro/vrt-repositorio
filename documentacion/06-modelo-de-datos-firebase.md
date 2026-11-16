# 06 - MODELO DE DATOS (FIREBASE REALTIME DATABASE)

Base de datos: `https://alvin-59045-default-rtdb.firebaseio.com/`

El acceso se hace por la **API REST** de Realtime Database: cada nodo se expone
como JSON en `{URL}/<ruta>.json`, lo que permite `GET / PUT / PATCH / POST /
DELETE` desde Python con `requests` (ver `core/services/firebase.py`).

## 6.1 Vision general de nodos

```
raiz/
├── users/        # cuentas de acceso (autenticacion propia)
├── players/      # roster de participantes
├── sessions/     # espejo de cada partida (por match_id)
└── events/       # telemetria (disparos, impactos, roster, partidas, sensores)
```

## 6.2 Nodo `users`

Clave: `user_key(username)` -> se normaliza a `[a-z0-9_-]` porque Realtime
Database prohibe `. $ # [ ] /` en las claves.

```
users/<clave>
  username       "jugador01"                 # nombre original
  display_name   "Jugador 01"                # nombre visible
  role           "operator" | "admin"
  active         true                        # si es false, no puede entrar
  password_hash  "pbkdf2_sha256$..."         # hash de Django (nunca texto plano)
  created_at     "2026-01-01T10:00:00-04:00"
  last_login     "2026-01-02T18:22:10-04:00"
```

**Seguridad**: la contrasena se guarda como hash **PBKDF2-SHA256** generado con
`django.contrib.auth.hashers.make_password` y se verifica con `check_password`.
Nunca se almacena en claro.

Repositorio: `blocks/accounts/repositories/users.py` (`UserRepository`).

Operaciones: `get`, `exists`, `list_all`, `count`, `create`, `verify`,
`touch_last_login`, `delete`.

## 6.3 Nodo `players`

Clave: generada por Firebase con `POST` (push key).

```
players/<pushKey>
  name        "Ana Quispe"
  team        "azul" | "rojo" | "verde" | "amarillo"
  status      "activo" | "inactivo"
  hits        0            # impactos acumulados
  shots       0            # disparos acumulados
  created_at  "2026-01-01T10:00:00-04:00"
```

Repositorio: `blocks/players/repositories/players.py` (`PlayerRepository`).

Operaciones: `list_all`, `count`, `get`, `create`, `set_status`, `delete`,
`bump_stats`.

## 6.4 Nodo `sessions`

Clave: el `match_id` de la partida (ej. `M-20260101-120000`). Es un **espejo**
de la partida; la fuente autoritativa es la sesion del navegador.

```
sessions/<match_id>
  active       true | false
  hp           100
  max_hp       100
  ammo         30
  max_ammo     30
  score        0
  shots        0
  hits         0
  match_id     "M-20260101-120000"
  started_at   "2026-01-01T12:00:00-04:00"
  finished_at  "" | "2026-01-01T12:05:00-04:00"
  last_kind    "disparo"
  last_detail  "Disparo detectado. Municion restante: 29."
  last_severity "info"
  actor        "jugador01"
  updated_at   "2026-01-01T12:00:05-04:00"
```

Repositorio: `blocks/simulation/repositories/sessions.py`
(`SessionRepository`). Operaciones: `save`, `get`, `count`.

## 6.5 Nodo `events`

Clave: generada por Firebase con `POST`. Como las push keys ordenan
cronologicamente, `orderBy="$key"` + `limitToLast` devuelve los mas recientes.

```
events/<pushKey>
  kind        "disparo" | "impacto" | "partida:inicio" | "partida:fin"
              | "roster:alta" | "roster:baja" | "roster:estado"
              | "jugador:eliminado" | "sensor:lectura" | ...
  detail      "Disparo detectado. Municion restante: 29."
  actor       "jugador01"
  severity    "info" | "success" | "warning" | "critical"
  source      "web" | "godot" | "esp32" | "mqtt" | "sistema"
  match_id    "M-20260101-120000"      # vacio si no pertenece a una partida
  created_at  "2026-01-01T12:00:00-04:00"
```

Repositorio: `blocks/telemetry/repositories/events.py` (`EventRepository`).
Servicio de escritura: `blocks/telemetry/services/recorder.py` (`EventRecorder`).

Operaciones: `append`, `recent(limit)`, `all`, `count`, `clear`, `by_match`.

## 6.6 Tipos de evento usados por la plataforma

| `kind` | Origen | Severidad tipica |
|--------|--------|------------------|
| `partida:inicio` | simulation | success |
| `disparo` | simulation | info |
| `impacto` | simulation | warning |
| `jugador:eliminado` | simulation | critical |
| `partida:fin` | simulation | success |
| `partida:reset` | simulation | info |
| `roster:alta` | players | info |
| `roster:baja` | players | warning |
| `roster:estado` | players | info / warning |
| `sensor:lectura` | IoT (ESP32) | info |

## 6.7 Consulta directa por REST (util para depurar)

```powershell
# Listar todos los usuarios
Invoke-RestMethod "https://alvin-59045-default-rtdb.firebaseio.com/users.json"

# Contar nodos (consulta superficial)
Invoke-RestMethod "https://alvin-59045-default-rtdb.firebaseio.com/players.json?shallow=true"

# Ver los ultimos eventos
Invoke-RestMethod "https://alvin-59045-default-rtdb.firebaseio.com/events.json?orderBy=`"`$key`"&limitToLast=5"
```

## 6.8 Consideraciones de seguridad

- El login se valida **contra el nodo `users`**, no contra Firebase Auth.
- La base esta **abierta** (sin token) para fines academicos.
- Para un entorno real:
  - usar **Firebase Authentication**, o
  - cerrar las reglas y configurar `FIREBASE_DB_SECRET` en `.env`.
