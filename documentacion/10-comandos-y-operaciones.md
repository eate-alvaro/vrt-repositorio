# 10 - COMANDOS Y OPERACIONES

Django permite comandos de gestion personalizados. Este proyecto define dos, en
`core/management/commands/`.

## 10.1 `firebase_check` - Diagnostico de conexion

Comprueba la conectividad con Realtime Database y cuenta los nodos principales.

```powershell
python manage.py firebase_check
```

Salida de ejemplo:

```
URL         : https://alvin-59045-default-rtdb.firebaseio.com/
Timeout     : 8.0 s
Credencial  : sin token (acceso publico)
----------------------------------------------------------
[OK]   conexion establecida (HTTP 200)
----------------------------------------------------------
[INFO] users     3 registro(s)
[INFO] players   5 registro(s)
[INFO] sessions  3 registro(s)
[INFO] events    6 registro(s)
----------------------------------------------------------
Diagnostico completado.
```

Nodos comprobados: `users`, `players`, `sessions`, `events`.

## 10.2 `seed_demo` - Datos de demostracion

Siembra usuarios, roster y eventos para usar la plataforma desde el primer
arranque.

```powershell
# Siembra completa (usuarios + roster + eventos)
python manage.py seed_demo

# Solo eventos de telemetria
python manage.py seed_demo --events-only

# Vaciar players y events antes de sembrar (no borra users)
python manage.py seed_demo --reset
```

### Usuarios creados

| Usuario | Contrasena | Nombre | Rol |
|---------|------------|--------|-----|
| `admin` | `admin1234` | Administrador | admin |
| `jugador01` | `1234` | Jugador 01 | operator |
| `jugador02` | `1234` | Jugador 02 | operator |

### Roster de ejemplo

Ana Quispe (azul), Luis Mamani (azul), Carla Rojas (rojo), Diego Vargas (rojo),
Elena Siles (verde).

### Eventos de ejemplo

`partida:inicio`, dos `disparo`, un `impacto`, un `roster:alta` y un
`sensor:lectura` (fuente `esp32`).

> Si un usuario ya existe, el comando lo informa como `[AVISO]` y continua.

## 10.3 Comandos estandar de Django

```powershell
# Comprobar la configuracion del proyecto
python manage.py check

# Aplicar migraciones de infraestructura (sesiones, mensajes)
python manage.py migrate

# Crear migraciones (no hay modelos de negocio en SQLite)
python manage.py makemigrations

# Servidor de desarrollo
python manage.py runserver 127.0.0.1:8765

# Consola interactiva (util para inspeccionar repositorios)
python manage.py shell

# Recoger estaticos para produccion
python manage.py collectstatic
```

## 10.4 Inspeccion rapida desde el shell

```powershell
python manage.py shell
```

```python
from blocks.accounts.repositories.users import UserRepository
from blocks.players.repositories.players import PlayerRepository
from blocks.telemetry.repositories.events import EventRepository
from blocks.simulation.repositories.sessions import SessionRepository

print("usuarios :", UserRepository().count())
print("jugadores:", PlayerRepository().count())
print("partidas :", SessionRepository().count())
print("eventos  :", EventRepository().count())

# Eliminar un usuario de prueba
UserRepository().delete("prueba_mvi")
```

## 10.5 Flujo de trabajo recomendado

1. `python manage.py check` antes de arrancar.
2. `python manage.py firebase_check` para confirmar la conexion.
3. `python manage.py seed_demo --events-only` si se vacio el historial y se
   quiere repoblar la demo.
4. `python manage.py runserver 127.0.0.1:8765`.
