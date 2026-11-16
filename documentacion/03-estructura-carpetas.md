# 03 - ESTRUCTURA DE CARPETAS

Arbol completo del proyecto, con el proposito de cada carpeta. Se omiten las
carpetas generadas (`.venv/`, `__pycache__/`).

```
VRT/
│
├── manage.py                       # Punto de entrada de Django
├── requirements.txt                # Dependencias Python
├── db.sqlite3                      # SQLite: SOLO sesiones y mensajes
├── .env                            # Configuracion local (no versionado)
├── .env.example                    # Plantilla de configuracion
├── .gitignore
├── iniciar_localhost.bat           # Arranque rapido del servidor local
├── README.md                       # Documentacion de raiz
├── Paintball_VR_IoT_Login_Demo.html# Prototipo original de un solo archivo
│
├── documentacion/                  # <<< ESTA CARPETA (documentacion .md)
│
├── config/                         # PROYECTO DJANGO
│   ├── settings.py                 # Apps, middleware, Firebase, TZ, logging
│   ├── urls.py                     # Enrutado raiz -> incluye cada bloque
│   ├── wsgi.py                     # Entrada WSGI
│   └── asgi.py                     # Entrada ASGI
│
├── core/                           # NUCLEO MVI REUTILIZABLE + INFRAESTRUCTURA
│   ├── mvi/
│   │   ├── intent.py               # Intent (base inmutable)
│   │   ├── effect.py               # Effect (base inmutable)
│   │   ├── state.py                # State (+ evolve)
│   │   ├── reducer.py              # Reducer + no_change
│   │   └── store.py                # Store (bucle de realimentacion)
│   ├── actor.py                    # Actor: identidad autenticada inmutable
│   ├── context_processors.py       # app_context (metadatos + ahora)
│   ├── http/
│   │   ├── middleware.py           # ActorMiddleware -> request.actor
│   │   ├── decorators.py           # login_required, safe_redirect_target, wants_partial
│   │   └── context.py              # page_context()
│   ├── services/
│   │   └── firebase.py             # Cliente REST de Realtime Database
│   └── management/
│       └── commands/
│           ├── firebase_check.py   # Diagnostico de conexion
│           └── seed_demo.py        # Datos de demostracion
│
├── theme/                          # BLOQUE DE TEMA Y ESTILOS (Tokyo Night)
│   ├── static/theme/css/
│   │   ├── tokens.css              # Paleta oficial + variables de diseno
│   │   ├── reset.css               # Normalizacion
│   │   ├── layout.css              # topbar / sidebar / workspace / statusline
│   │   └── components.css          # paneles, botones, tablas, medidores, login
│   ├── templates/theme/
│   │   ├── base.html               # Layout del workspace (app)
│   │   ├── auth_base.html          # Layout de acceso (login/registro)
│   │   └── partials/
│   │       ├── topbar.html
│   │       ├── sidebar.html
│   │       ├── statusline.html
│   │       └── messages.html
│   ├── templatetags/
│   │   └── ui.py                   # {% icon %}, severity_class, percent, ascii_state
│   ├── navigation.py               # Navegacion global del workspace
│   ├── context_processors.py       # theme_context (nombre de app, tema, nav)
│   └── apps.py
│
├── blocks/                         # BLOQUES FUNCIONALES (una app Django cada uno)
│   ├── accounts/                   # Autenticacion contra el nodo users
│   │   ├── mvi/                    # context, state, intents, effects, reducer, handlers, store
│   │   ├── repositories/users.py   # UserRepository (hash PBKDF2)
│   │   ├── templates/blocks/accounts/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── urls.py
│   │   └── views.py                # login / register / logout
│   │
│   ├── telemetry/                  # DOMINIO COMPARTIDO de eventos
│   │   ├── models.py               # EventRecord
│   │   ├── repositories/events.py  # EventRepository (nodo events)
│   │   └── services/recorder.py    # EventRecorder
│   │
│   ├── dashboard/                  # Panel principal
│   │   ├── mvi/                    # context(handlers), state, intents, effects, reducer, store
│   │   ├── services/snapshot.py    # DashboardService (consolida players+events+sessions)
│   │   ├── templates/blocks/dashboard/
│   │   │   ├── index.html
│   │   │   ├── about.html
│   │   │   └── partials/{dashboard_view,summary_panel}.html
│   │   ├── urls.py
│   │   └── views.py                # index / about
│   │
│   ├── simulation/                 # Maquina de estados de la partida
│   │   ├── mvi/
│   │   ├── repositories/sessions.py# SessionRepository (nodo sessions)
│   │   ├── services/session.py     # load/save/clear de la partida en sesion
│   │   ├── templates/blocks/simulation/
│   │   │   ├── index.html
│   │   │   └── partials/{match_view,match_panel}.html
│   │   ├── urls.py
│   │   └── views.py                # index / action (despachador de intents)
│   │
│   ├── players/                    # Roster (nodo players)
│   │   ├── mvi/
│   │   ├── repositories/players.py # PlayerRepository
│   │   ├── models.py               # PlayerRecord
│   │   ├── templates/blocks/players/
│   │   │   ├── index.html
│   │   │   └── partials/{roster_view,roster_panel}.html
│   │   ├── urls.py
│   │   └── views.py                # index / add / toggle / remove
│   │
│   └── history/                    # Visor de telemetria (nodo events)
│       ├── mvi/
│       ├── templates/blocks/history/
│       │   ├── index.html
│       │   └── partials/{history_view,events_panel}.html
│       ├── urls.py
│       └── views.py                # index / clear
│
└── templates/                      # Plantillas globales de error
    ├── 404.html
    └── 500.html
```

## 3.1 Reglas de organizacion

1. **`config/`** solo contiene configuracion del proyecto (no logica de negocio).
2. **`core/`** es reutilizable: no conoce ningun bloque funcional.
3. **`theme/`** es el unico lugar donde vive el estilo y la presentacion global.
4. **`blocks/<x>/`** es una app Django autocontenida. Ningun bloque importa de
   otro bloque excepto `telemetry` (dominio compartido) y el `dashboard` (que
   consolida a los demas).
5. **`templates/`** en la raiz guarda solo las paginas de error 404/500.

## 3.2 Patron interno de un bloque funcional

```
blocks/<bloque>/
├── __init__.py
├── apps.py                 # AppConfig
├── models.py               # Dominio inmutable (si aplica)
├── mvi/                    # Ciclo MVI del bloque
├── repositories/           # Acceso a Realtime Database
├── services/               # Logica de dominio adicional
├── templates/blocks/<bloque>/
│   ├── index.html          # Pagina completa (extends theme/base.html)
│   └── partials/
│       ├── <bloque>_view.html   # Envoltorio: cabecera + panel (objetivo HTMX)
│       └── <panel>.html         # Panel interno
├── urls.py                 # app_name = "<bloque>"
└── views.py                # Intent dispatcher
```

La separacion `*_view.html` / `*_panel.html` permite que HTMX reemplace todo el
envoltorio y asi se actualicen tambien las insignias de la cabecera.
