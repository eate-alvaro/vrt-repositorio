@echo off
title PAINTBALL VR ^& IOT - servidor local
cd /d "C:\Users\USUARIO\OneDrive\Documents\VRT"

echo ==========================================================
echo   PAINTBALL VR ^& IOT  -  servidor local
echo   http://127.0.0.1:8765/
echo   Cierra esta ventana para detener el servidor.
echo ==========================================================
echo.

rem Abre el navegador unos segundos despues de arrancar el servidor
start "" cmd /c "timeout /t 3 /nobreak >nul & start "" http://127.0.0.1:8765/"

.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8765
