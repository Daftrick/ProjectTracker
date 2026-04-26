Dim WshShell
Set WshShell = CreateObject("WScript.Shell")

' Cambiar directorio de trabajo al de la app
WshShell.CurrentDirectory = "H:\My Drive\Omniious\Claude Code\ProjectTracker"

' Instalar dependencias silenciosamente (espera a que termine)
WshShell.Run """C:\Users\daftr\AppData\Local\Python\pythoncore-3.14-64\python.exe"" -m pip install flask fpdf2 --quiet", 0, True

' Abrir navegador tras unos segundos (ventana oculta)
WshShell.Run "cmd /c ping 127.0.0.1 -n 4 >nul && start """" ""http://localhost:8080""", 0, False

' Iniciar Flask en segundo plano (sin ventana visible)
WshShell.Run """C:\Users\daftr\AppData\Local\Python\pythoncore-3.14-64\python.exe"" app.py", 0, False
