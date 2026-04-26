@echo off
REM Cambiar al directorio donde está este .bat (esencial para doble clic)
cd /d "%~dp0"

set "APP_PORT=8080"
set "APP_URL=http://localhost:8080"
set "OPEN_BROWSER=1"
if /I "%~1"=="noopen" set "OPEN_BROWSER=0"

echo =============================================
echo    Project Tracker - Iniciando...
echo =============================================
echo.

REM Verificar si pip está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instala Python 3.8+ desde python.org
    pause
    exit /b 1
)

set "PYTHON=C:\Users\daftr\AppData\Local\Python\pythoncore-3.14-64\python.exe"

powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Get-NetTCPConnection -LocalPort %APP_PORT% -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>&1
if not errorlevel 1 goto already_running

REM Instalar Flask con el mismo Python que corre la app
echo Verificando dependencias...
"%PYTHON%" -m pip install flask fpdf2 --quiet

echo.
echo Iniciando servidor en %APP_URL%
echo Para detener: presiona Ctrl+C
echo.
if "%OPEN_BROWSER%"=="1" start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process '%APP_URL%'"
"%PYTHON%" app.py

pause
exit /b 0

:already_running
echo Project Tracker ya esta corriendo en %APP_URL%
echo No se abrira otra pestana ni otra instancia.
exit /b 0
