@echo off
REM ============================================================
REM  REINICIAR.bat - Mata Python y relanza Project Tracker
REM  Usa INICIAR.vbs (silencioso) si existe, sino INICIAR.bat
REM ============================================================
cd /d "%~dp0"

REM -- Terminar cualquier instancia de Python corriendo --
taskkill /f /im python.exe  /t >nul 2>&1
taskkill /f /im pythonw.exe /t >nul 2>&1

REM -- Esperar 2 segundos --
timeout /t 2 /nobreak >nul

REM -- Relanzar: VBS preferido (sin ventana), bat como fallback --
if exist "%~dp0INICIAR.vbs" (
    wscript.exe "%~dp0INICIAR.vbs"
) else (
    start "" "%~dp0INICIAR.bat"
)
