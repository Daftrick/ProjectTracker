import shutil
import subprocess
import sys


COMMANDS = {
    "update": "update",
    "check-update": "check-update",
}


def main(argv=None, which=shutil.which, run=subprocess.run):
    argv = list(sys.argv[1:] if argv is None else argv)
    action = argv[0] if argv else "update"
    command = COMMANDS.get(action)
    if command is None:
        print(f"Uso: python tools/graphify_task.py {'|'.join(COMMANDS)}", file=sys.stderr)
        return 2

    graphify = which("graphify")
    if not graphify:
        print("[graphify] graphify no esta instalado/en PATH; se omite la actualizacion local.")
        return 0

    result = run([graphify, command, "."], check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
