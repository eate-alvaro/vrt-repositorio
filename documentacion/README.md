# DOCUMENTACION - PAINTBALL VR & IOT

Documentacion tecnica del proyecto **"Modelo de realidad virtual e IoT para la
simulacion interactiva de paintball en entornos controlados"**.

Esta carpeta concentra toda la documentacion en archivos Markdown. El objetivo
es que cualquier persona (o evaluador) pueda entender **con que esta construido
el proyecto, como esta estructurado, como se lanza y como se conectan los
modulos** sin necesidad de leer todo el codigo.

---

## Indice de documentos

| # | Archivo | Contenido |
|---|---------|-----------|
| 01 | [01-vision-general.md](01-vision-general.md) | Objetivo, alcance, stack tecnologico, lenguajes y estado |
| 02 | [02-arquitectura-mvi.md](02-arquitectura-mvi.md) | El patron MVI: Intent, State, Reducer, Effect, Store |
| 03 | [03-estructura-carpetas.md](03-estructura-carpetas.md) | Arbol completo de carpetas comentado |
| 04 | [04-bloques-y-modulos.md](04-bloques-y-modulos.md) | Cada bloque funcional: proposito, MVI y piezas |
| 05 | [05-mapa-de-conexiones.md](05-mapa-de-conexiones.md) | Grafo de dependencias entre modulos y bloques |
| 06 | [06-modelo-de-datos-firebase.md](06-modelo-de-datos-firebase.md) | Esquema de nodos de Realtime Database |
| 07 | [07-tema-y-frontend.md](07-tema-y-frontend.md) | Tema Tokyo Night, CSS, iconos y HTMX |
| 08 | [08-instalacion-y-ejecucion.md](08-instalacion-y-ejecucion.md) | Instalacion, lanzamiento y arranque automatico |
| 09 | [09-referencia-de-rutas.md](09-referencia-de-rutas.md) | Tabla de URLs, namespaces, metodos e intents |
| 10 | [10-comandos-y-operaciones.md](10-comandos-y-operaciones.md) | Comandos de gestion y diagnostico |
| 11 | [11-integracion-vr-iot.md](11-integracion-vr-iot.md) | Conexion prevista con Godot, ESP32 y MQTT |
| 12 | [12-glosario.md](12-glosario.md) | Glosario de terminos y convenciones |

---

## Resumen en una linea

> Plataforma web de centro de control para simulacion de paintball, construida
> con **Django + Python** bajo una arquitectura **MVI por bloques**, con
> persistencia de estado en **Firebase Realtime Database** y una interfaz
> **Tokyo Night / Omarchy OS** (estilo tiling window manager) que funciona con y
> sin JavaScript gracias a **HTMX**.

---

## Datos rapidos

| Dato | Valor |
|------|-------|
| Lenguaje principal | Python 3.14 |
| Framework web | Django 6.1 |
| Patron de arquitectura | MVI (Model - View - Intent) por bloques |
| Persistencia de dominio | Firebase Realtime Database (API REST) |
| Persistencia de infraestructura | SQLite (sesiones y mensajes) |
| Frontend | HTML + CSS propio + HTMX 2.0.4 |
| Tema visual | Tokyo Night (Night & Storm) / Omarchy OS |
| Zona horaria | America/La_Paz |
| Idioma | Espanol |
| Base de datos RTDB | `https://alvin-59045-default-rtdb.firebaseio.com/` |
| URL local | `http://127.0.0.1:8765/` |

---

> Nota: este proyecto es de caracter **academico**. La Realtime Database esta
> abierta sin autenticacion (sin token). En un entorno real se debe usar
> Firebase Auth o reglas cerradas.
