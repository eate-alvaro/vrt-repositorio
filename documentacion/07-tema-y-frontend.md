# 07 - TEMA Y FRONTEND (TOKYO NIGHT / OMARCHY OS)

Todo el estilo vive en el bloque `theme`. Ningun otro bloque escribe CSS ni
define colores.

## 7.1 Filosofia visual

La interfaz imita un **tiling window manager** (estetica Omarchy OS) con la
paleta **Tokyo Night**. Reglas estrictas:

- **Cero emojis.**
- Indicadores **ASCII puro**: `>`, `::`, `[x]`, `[ ]`, `-`, `*`.
- O bien **iconos SVG monocromaticos de trazo fino** (`stroke-width: 1.5`).
- Contenedores rectangulares: `border-radius` entre 0 y 4 px.
- Separadores de `1px solid`.
- `box-shadow: none` (nada de sombras decorativas).
- Tipografia **monoespaciada** y alta densidad de informacion.
- Interacciones `:hover` / `:focus` **instantaneas** (sin transiciones lentas).

## 7.2 Paleta y tokens

Archivo: `theme/static/theme/css/tokens.css`. Define las variables de color de
Tokyo Night (variantes **Night** y **Storm**) y los tokens de diseno (espaciado,
tipografia, bordes). Los demas archivos CSS consumen esas variables, por lo que
cambiar la paleta es tocar un solo archivo.

## 7.3 Hojas de estilo (orden de carga)

| Archivo | Responsabilidad |
|---------|-----------------|
| `tokens.css` | Paleta y variables de diseno |
| `reset.css` | Normalizacion (margenes, box-sizing, tipografia base) |
| `layout.css` | `topbar`, `sidebar`, `workspace`, `statusline` |
| `components.css` | Paneles, botones, tablas, insignias, medidores, pantalla de acceso |

`theme/templates/theme/base.html` carga las cuatro en ese orden.

## 7.4 Estructura visual (workspace)

```
+----------------------------------------------------------+
| topbar     marca + sesion del usuario                     |
+----------+-----------------------------------------------+
| sidebar  | workspace                                     |
| modulos  |   mensajes flash                              |
|          |   contenido del bloque (page-head + paneles)  |
+----------+-----------------------------------------------+
| statusline  estado MVI | nodo RTDB | usuario | hora        |
+----------------------------------------------------------+
```

- **`topbar`** (`partials/topbar.html`): marca de la app y datos de la sesion.
- **`sidebar`** (`partials/sidebar.html`): navegacion generada por
  `theme/navigation.py`.
- **`workspace`**: donde cada bloque inyecta su `{% block content %}`.
- **`statusline`** (`partials/statusline.html`): linea de estado inferior.
- **`messages`** (`partials/messages.html`): mensajes flash de Django.

## 7.5 Pantalla de acceso

`theme/templates/theme/auth_base.html` es un layout aparte (sin sidebar ni
statusline) para login y registro. Incluye la marca, el host de la RTDB y el
nombre del tema.

## 7.6 Iconografia (sin emojis)

Etiqueta `{% icon %}` en `theme/templatetags/ui.py`:

```django
{% icon "crosshair" 16 1.5 %}
```

- Trazos definidos en una grilla de 24x24 (`path`, `circle`).
- Renderiza `<svg>` con `stroke="currentColor"`, `stroke-width=1.5`,
  `fill="none"`, `aria-hidden="true"`.
- Iconos disponibles: `grid`, `crosshair`, `users`, `clock`, `info`, `power`,
  `login`, `plus`, `minus`, `refresh`, `trash`, `target`, `bolt`, `shield`,
  `activity`, `terminal`, `check`, `x`, `user`, `flag`, `list`, `database`,
  `play`, `stop`, `chevron`, `layers`, `wifi`, `wifi-off`, `lock`.

Otros filtros/etiquetas utiles:

| Etiqueta / filtro | Uso |
|-------------------|-----|
| `{{ valor\|severity_class }}` | Clase CSS segun severidad (`is-info`, `is-warning`, ...) |
| `{{ parte\|percent:total }}` | Porcentaje entero acotado a [0, 100] |
| `{% ascii_state flag %}` | `[x] ACTIVO` / `[ ] INACTIVO` |

## 7.7 HTMX (interaccion sin recargar)

HTMX 2.0.4 se carga desde CDN en `base.html`. Se usa para actualizar paneles de
forma parcial:

- Cada bloque expone una constante `PARTIAL` que apunta a un **envoltorio**
  `*_view.html` (cabecera + panel).
- Los controles usan `hx-post` / `hx-get` con `hx-target="#<bloque>-view"` y
  `hx-swap="outerHTML"`.
- El CSRF se envia con `hx-headers` en `<body>`.

**Degradacion elegante**: todos los formularios conservan `method="post"
action="..."`, de modo que la plataforma **funciona igual sin JavaScript**
(recarga completa de la pagina).

Objetivos HTMX por bloque:

| Bloque | Objetivo | Envoltorio |
|--------|----------|------------|
| simulation | `#match-view` | `partials/match_view.html` |
| players | `#roster-view` | `partials/roster_view.html` |
| history | `#history-view` | `partials/history_view.html` |
| dashboard | `#dashboard-view` | `partials/dashboard_view.html` |

El patron `*_view.html` (envoltorio) + `*_panel.html` (panel interno) existe
para que al refrescar tambien se actualicen las **insignias de la cabecera**.

## 7.8 Convenciones de marcado

- Estructura de pagina: `page-head` (eyebrow + titulo + subtitulo + acciones),
  seguido de uno o varios `panel`.
- Estados con clases utilitarias: `badge--info`, `badge--success`,
  `badge--muted`, `badge--danger`, `dot--online`, `dot--offline`.
- Avisos al usuario: componente `notice` (`notice--error`, etc.).
- Tablas: `.table`, con `.table__empty` para el estado vacio.
- Medidores: `.stat` / `.stat__value` para las metricas.
