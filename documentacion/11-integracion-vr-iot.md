# 11 - INTEGRACION VR + IOT

La plataforma esta disenada para ser el **punto de convergencia** de tres
fuentes: la web, el entorno de realidad virtual y los dispositivos IoT.

## 11.1 Principio de integracion

Todos los componentes escriben en el **mismo nodo `events`** de Realtime
Database, distinguiendose por el campo `source`:

| `source` | Origen |
|----------|--------|
| `web` | La propia plataforma Django |
| `godot` | Entorno de realidad virtual (Godot) |
| `esp32` | Dispositivos IoT (sensores en chalecos/marcadores) |
| `mqtt` | Broker MQTT (puente IoT) |
| `sistema` | Procesos internos |

Como el nodo `events` es comun, **cualquier evento publicado aparece
automaticamente** en el Historial y en el Panel principal, sin cambios en el
codigo de la plataforma.

## 11.2 Esquema de publicacion

Un componente externo solo debe hacer `POST` a:

```
https://alvin-59045-default-rtdb.firebaseio.com/events.json
```

con un cuerpo JSON con la forma de `events/<pushKey>`:

```json
{
  "kind": "sensor:lectura",
  "detail": "ESP32 reporto 12 impactos en el chaleco 03.",
  "actor": "jugador01",
  "severity": "info",
  "source": "esp32",
  "match_id": "M-20260101-120000",
  "created_at": "2026-01-01T12:00:00-04:00"
}
```

## 11.3 Godot (realidad virtual)

- El entorno VR genera jugadas (disparos, impactos, inicio/fin de ronda).
- Publica cada jugada en `events` con `source: "godot"`.
- Puede leer el estado de la partida desde el nodo `sessions/<match_id>` para
  sincronizarse con la plataforma.
- Implementacion sugerida: `HTTPRequest` de Godot contra la API REST de
  Realtime Database.

## 11.4 ESP32 / sensores (IoT)

- Sensores en chalecos detectan impactos; marcadores detectan disparos.
- El firmware publica en `events` con `source: "esp32"`.
- Severidad sugerida: `impacto` -> `warning`, `jugador:eliminado` ->
  `critical`.
- Alternativa: el ESP32 publica en un broker **MQTT** y un puente publica en
  Firebase con `source: "mqtt"`.

## 11.5 Flujo de datos integrado

```
   +----------+        +-----------+        +------------------+
   |  Godot   |        |   ESP32   |        |  Plataforma web  |
   |  (VR)    |        |  (IoT)    |        |     (Django)     |
   +----+-----+        +-----+-----+        +--------+---------+
        |                    |                       |
        |  POST events       |  POST events          |  POST events
        |  source=godot      |  source=esp32         |  source=web
        v                    v                       v
   +-------------------------------------------------------------+
   |            Firebase Realtime Database  /events              |
   +----------------------------+--------------------------------+
                                |
                                | lectura (orderBy $key, limitToLast)
                                v
                +-----------------------------------+
                |  Plataforma Django                |
                |   - Historial (filtro severidad)  |
                |   - Panel principal (consolidado) |
                +-----------------------------------+
```

## 11.6 Puntos de extension previstos

| Extension | Donde tocar |
|-----------|-------------|
| Nuevo origen de datos | Publicar en `events` con un `source` nuevo (agregar a `SOURCES` en `blocks/telemetry/models.py`) |
| Nueva severidad | Agregar a `SEVERITIES` y a `FILTERS` en `blocks/history/mvi/state.py` |
| Sincronizar partida con VR | Leer/escribir `sessions/<match_id>` desde el cliente |
| Webhook de entrada | Crear una vista que reciba POST y use `EventRecorder.record(...)` |
| Panel en vivo | Reemplazar el refresco manual por HTMX con `hx-trigger="every Ns"` |

## 11.7 Recomendaciones para produccion

- Cerrar las reglas de Realtime Database y configurar `FIREBASE_DB_SECRET`.
- Usar **Firebase Authentication** en lugar del login contra el nodo `users`.
- Anadir un servicio intermedio (Cloud Functions o similar) para validar los
  eventos de dispositivos externos antes de escribirlos.
- Limitar el crecimiento del nodo `events` (rotacion o archivado).
