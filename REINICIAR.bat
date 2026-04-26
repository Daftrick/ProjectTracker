@echo off
REM ============================================================
REM  REINICIAR.bat - Reinicia Project Tracker sin abrir otra pestana
REM  Usa INICIAR.vbs (silencioso) si existe, sino INICIAR.bat
REM ============================================================
cd /d "%~dp0"

set APP_PORT=8080

REM -- Terminar solo el proceso que escucha en el puerto de Project Tracker --
for /f %%P in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$c = Get-NetTCPConnection -LocalPort %APP_PORT% -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1; if ($c) { $c.OwningProcess }"') do (
    taskkill /f /pid %%P /t >nul 2>&1
)

REM -- Esperar 2 segundos --
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 2" >nul 2>&1

REM -- Relanzar sin abrir navegador: VBS preferido (sin ventana), bat como fallback --
if exist "%~dp0INICIAR.vbs" (
    wscript.exe "%~dp0INICIAR.vbs" noopen
) else (
    start "" "%~dp0INICIAR.bat" noopen
)
