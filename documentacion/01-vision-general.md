# 01 - VISION GENERAL

## 1.1 Nombre del proyecto

**PAINTBALL VR & IOT** - plataforma de simulacion.

Titulo academico completo:

> *"Modelo de realidad virtual e IoT para la simulacion interactiva de paintball
> en entornos controlados."*

## 1.2 Objetivo

Construir el **centro de control** de un sistema de paintball simulado que
integra:

- un **entorno de realidad virtual** (previsto en Godot) que produce jugadas,
- **dispositivos IoT** (previsto ESP32 con sensores en chalecos y marcadores),
- una **capa web** que autentica usuarios, administra el roster, dirige la
  partida y registra toda la telemetria.

La plataforma es la fuente de verdad de la sesion de juego y el punto donde se
consolidan los datos de los otros dos mundos.

## 1.3 Alcance funcional (lo que ya existe)

| Modulo | Que hace |
|--------|----------|
| Acceso | Login y registro contra el nodo `users` de Realtime Database |
| Panel principal | Consolida jugadores, eventos y partidas + estado de conexion |
| Simulacion | Maquina de estados de la partida (iniciar, disparar, impacto, finalizar, reiniciar) |
| Jugadores | Roster (alta, baja, activar/pausar) sincronizado con el nodo `players` |
| Historial | Visor de telemetria del nodo `events` con filtro por severidad |
| Proyecto | Pagina de documentacion dentro de la aplicacion |

## 1.4 Stack tecnologico

### Lenguajes

| Capa | Lenguaje | Uso |
|------|----------|-----|
| Servidor | **Python 3.14** | Toda la logica de negocio, MVI, acceso a datos |
| Plantillas | **HTML + Django Template Language** | Vistas (View en MVI) |
| Estilos | **CSS 3** (escrito a mano) | Tema Tokyo Night, sin frameworks |
| Interaccion | **JavaScript minimo** (solo HTMX) | Actualizacion parcial de paneles |

### Framework y librerias

| Dependencia | Version | Rol |
|-------------|---------|-----|
| **Django** | 6.1.3 | Framework web: enrutado, plantillas, sesiones, middleware |
| requests | 2.34.2 | Cliente HTTP hacia la API REST de Realtime Database |
| python-dotenv | 1.x | Carga de variables de entorno desde `.env` |
| whitenoise | 6.x | Servicio de archivos estaticos |
| HTMX | 2.0.4 (CDN) | Actualizacion de paneles sin recargar la pagina |

> Las dependencias Python se declaran en `requirements.txt` con los rangos
> `Django>=5.2,<7.0`, `requests>=2.32`, `python-dotenv>=1.0`,
> `whitenoise>=6.7`. Se fijo **Django 6.x** porque Django 5.2 no soporta
> Python 3.14.

### Persistencia

| Almacen | Contenido | Tecnologia |
|---------|-----------|------------|
| **Firebase Realtime Database** | Estado de dominio: usuarios, jugadores, partidas, eventos | API REST (`*.json`) |
| **SQLite** (`db.sqlite3`) | Solo infraestructura de Django: sesiones y mensajes | `django.db.backends.sqlite3` |

La base SQLite **no guarda datos de negocio**: sirve unicamente para que Django
gestione la sesion del navegador y los mensajes flash.

## 1.5 Estilo de arquitectura

El proyecto sigue **MVI (Model - View - Intent)** con dos decisiones clave:

1. **MVI por bloques funcionales**: cada feature (cuentas, jugadores,
   simulacion, historial, panel) es una app Django independiente con su propio
   ciclo MVI.
2. **MVI en el servidor**: no hay un store en el navegador. La *vista* actua
   como despachador de intents, la *plantilla* es la View, y la *sesion /
   Realtime Database* es la persistencia.

Ver detalle en [02-arquitectura-mvi.md](02-arquitectura-mvi.md).

## 1.6 Estado del proyecto

- Version: **1.0.0**
- Estado: funcional y verificado de extremo a extremo (login, registro,
  simulacion, roster, historial y panel).
- Datos de demostracion sembrados via `python manage.py seed_demo`.

## 1.7 Requisitos del entorno

- **Python 3.13 o superior** (probado con 3.14.2).
- Acceso a internet (la Realtime Database es remota).
- Reglas de lectura/escritura habilitadas en el nodo raiz del proyecto.
- Navegador moderno (Chrome, Edge, Firefox).

## 1.8 Convenciones del codigo

- **Idioma**: identificadores y textos en espanol; codigo sin tildes ni
  caracteres no ASCII (para evitar problemas de codificacion).
- **Inmutabilidad**: los estados, intents y efectos son `@dataclass(frozen=True)`.
- **Sin emojis** en la interfaz ni en los archivos: los indicadores visuales son
  ASCII puro (`>`, `::`, `[x]`, `-`, `*`) o iconos SVG de trazo fino.
- **Separacion estricta**: el reducer nunca hace IO; la IO vive en `handlers.py`.
