# 08 - INSTALACION Y EJECUCION

## 8.1 Requisitos

- **Python 3.13 o superior** (probado con 3.14.2).
- Acceso a internet (la Realtime Database es remota).
- Navegador moderno.

## 8.2 Instalacion paso a paso

```powershell
# 1) Ir a la carpeta del proyecto
cd "C:\Users\USUARIO\OneDrive\Documents\VRT"

# 2) Crear el entorno virtual
python -m venv .venv

# 3) Activar el entorno virtual
.\.venv\Scripts\Activate.ps1

# 4) Instalar dependencias
pip install -r requirements.txt

# 5) Configuracion de entorno
Copy-Item .env.example .env
#   Edita .env si necesitas cambiar la URL o el token de Firebase.

# 6) Infraestructura de Django (sesiones y mensajes)
python manage.py migrate

# 7) Verificar la conexion con Firebase
python manage.py firebase_check

# 8) Sembrar datos de demostracion (usuarios, roster y eventos)
python manage.py seed_demo
```

## 8.3 Variables de entorno (`.env`)

| Variable | Descripcion | Valor por defecto |
|----------|-------------|-------------------|
| `DJANGO_SECRET_KEY` | Clave secreta de Django | `dev-insecure-change-me-in-production` |
| `DJANGO_DEBUG` | Modo depuracion (1/0) | `1` |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos (coma) | `127.0.0.1,localhost` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origenes CSRF de confianza | vacio |
| `FIREBASE_DB_URL` | URL de Realtime Database | `https://alvin-59045-default-rtdb.firebaseio.com/` |
| `FIREBASE_DB_SECRET` | Token para reglas cerradas (opcional) | vacio |
| `FIREBASE_TIMEOUT` | Timeout de red (segundos) | `8` |
| `FIREBASE_USERS_NODE` | Nombre del nodo de usuarios | `users` |
| `VRT_APP_NAME` | Nombre visible de la app | `PAINTBALL VR & IOT` |
| `VRT_APP_TAGLINE` | Lema de la app | `PLATAFORMA DE SIMULACION` |
| `VRT_APP_VERSION` | Version mostrada | `1.0.0` |

## 8.4 Lanzamiento del servidor

### Opcion A - Comando manual (PowerShell)

```powershell
cd "C:\Users\USUARIO\OneDrive\Documents\VRT"
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8765
```

O activando el entorno primero:

```powershell
cd "C:\Users\USUARIO\OneDrive\Documents\VRT"
.\.venv\Scripts\Activate.ps1
python manage.py runserver 127.0.0.1:8765
```

Luego abre: **http://127.0.0.1:8765/**

Para detener: `Ctrl + C`.

### Opcion B - Doble clic

El archivo `iniciar_localhost.bat` de la raiz hace todo: entra a la carpeta,
abre el navegador a los 3 segundos y levanta el servidor.

> Cerrar la ventana negra = detener el servidor.

### Opcion C - Arranque automatico al iniciar Windows

Se creo un acceso directo en la carpeta de Inicio de Windows:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\PAINTBALL VR e IOT.lnk
```

Al iniciar sesion en Windows, el servidor arranca solo (minimizado).

**Desactivarlo**: `Win + R` -> `shell:startup` -> borrar el acceso directo.

**Abrir la carpeta de Inicio**:

```powershell
explorer "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
```

## 8.5 Credenciales de demostracion

| Usuario | Contrasena | Rol |
|---------|------------|-----|
| `admin` | `admin1234` | admin |
| `jugador01` | `1234` | operator |
| `jugador02` | `1234` | operator |

Tambien se pueden crear cuentas nuevas desde **Crear cuenta** (se registran en
el nodo `users` de Realtime Database).

## 8.6 Flujo de uso

1. Abre `http://127.0.0.1:8765/` -> redirige a `/cuenta/entrar/`.
2. Inicia sesion (o crea una cuenta).
3. **Panel principal**: resumen del sistema.
4. **Simulacion**: iniciar -> disparar -> impacto -> finalizar.
5. **Jugadores**: agregar / pausar / quitar.
6. **Historial**: filtrar por severidad, vaciar.

## 8.7 Notas sobre el servidor de desarrollo

- Es el servidor de desarrollo de Django: suficiente para la demo academica.
- Para exponerlo a otros equipos de la red: usar `0.0.0.0:8765` en vez de
  `127.0.0.1:8765` y permitir el puerto en el Firewall de Windows.
- `manage.py runserver` recarga solo al editar Python. Si se usa `--noreload`,
  hay que reiniciar el proceso manualmente para tomar cambios de Python (las
  plantillas si se recargan en vivo).

## 8.8 Solucion de problemas

| Sintoma | Causa probable | Solucion |
|---------|----------------|----------|
| `502`/`sin respuesta` al abrir | El servidor aun arranca | Esperar unos segundos y recargar |
| "No se pudo consultar Firebase" | Sin internet o reglas cerradas | Revisar conexion y reglas del nodo |
| "Usuario o contrasena incorrectos" | Credenciales mal escritas o usuario inactivo | Verificar credenciales; `active=true` |
| `ModuleNotFoundError` | Entorno virtual no activado | Activar `.venv` o usar `.\.venv\Scripts\python.exe` |
| Puerto ocupado | Otro proceso usa 8765 | Cambiar de puerto o cerrar el proceso |
| Cambios de Python no se ven | Se arranco con `--noreload` | Reiniciar el proceso |
