Dim WshShell
Set WshShell = CreateObject("WScript.Shell")

Const APP_PORT = "8080"
Const APP_URL = "http://localhost:8080"
Const PYTHON_EXE = "C:\Users\daftr\AppData\Local\Python\pythoncore-3.14-64\python.exe"

Dim openBrowser
openBrowser = True
If WScript.Arguments.Count > 0 Then
    If LCase(WScript.Arguments(0)) = "noopen" Then openBrowser = False
End If

' Cambiar directorio de trabajo al de la app
WshShell.CurrentDirectory = "H:\My Drive\Omniious\Claude Code\ProjectTracker"

' Si la app ya esta corriendo, no abrir otra pestana ni crear otra instancia.
If IsPortListening(APP_PORT) Then
    WScript.Quit 0
End If

' Instalar dependencias silenciosamente (espera a que termine)
WshShell.Run """" & PYTHON_EXE & """ -m pip install flask fpdf2 --quiet", 0, True

' Abrir navegador tras unos segundos, solo cuando se pidio abrir UI.
If openBrowser Then
    WshShell.Run "cmd /c ping 127.0.0.1 -n 4 >nul && start """" """ & APP_URL & """", 0, False
End If

' Iniciar Flask en segundo plano (sin ventana visible)
WshShell.Run """" & PYTHON_EXE & """ app.py", 0, False

Function IsPortListening(port)
    Dim cmd, exitCode
    cmd = "powershell -NoProfile -ExecutionPolicy Bypass -Command " & _
          """if (Get-NetTCPConnection -LocalPort " & port & " -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"""
    exitCode = WshShell.Run(cmd, 0, True)
    IsPortListening = (exitCode = 0)
End Function
