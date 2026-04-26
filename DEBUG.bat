@echo off
cd /d "%~dp0"

echo =============================================
echo    Project Tracker - MODO DEBUG
echo    Auto-reload activo: edita .py y se recarga
echo    Los errores se muestran aqui
echo =============================================
echo.

set PYTHON=C:\Users\daftr\AppData\Local\Python\pythoncore-3.14-64\python.exe
set FLASK_DEBUG=1

echo Verificando dependencias...
"%PYTHON%" -m pip install flask fpdf2 --quiet

echo.
echo Servidor en http://localhost:8080
echo Para detener: Ctrl+C
echo.
ping 127.0.0.1 -n 4 >nul & start "" "http://localhost:8080"
"%PYTHON%" app.py

pause
