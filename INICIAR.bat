@echo off
REM Cambiar al directorio donde está este .bat (esencial para doble clic)
cd /d "%~dp0"

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

set PYTHON=C:\Users\daftr\AppData\Local\Python\pythoncore-3.14-64\python.exe

REM Instalar Flask con el mismo Python que corre la app
echo Verificando dependencias...
"%PYTHON%" -m pip install flask --quiet

echo.
echo Iniciando servidor en http://localhost:8080
echo Para detener: presiona Ctrl+C
echo.
ping 127.0.0.1 -n 4 >nul & start "" "http://localhost:8080"
"%PYTHON%" app.py

pause
