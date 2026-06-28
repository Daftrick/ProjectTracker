#!/usr/bin/env python3

from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def _run_graphify(args, runner, which):
    graphify = which("graphify")
    if not graphify:
        print("[graphify] no hay binario graphify real disponible; se omite la actualizacion local.")
        return 0

    try:
        completed = runner([graphify, *args], cwd=ROOT)
    except OSError as exc:
        print(f"[graphify] no se pudo ejecutar {graphify}: {exc}", file=sys.stderr)
        return 1
    return completed.returncode


def main(argv=None, runner=subprocess.run, which=shutil.which):
    argv = list(sys.argv[1:] if argv is None else argv)
    action = argv[0] if argv else "update"
    if action == "update":
        target = argv[1] if len(argv) > 1 else "."
        return _run_graphify(["update", target], runner, which)
    if action == "check-update":
        return _run_graphify(["info"], runner, which)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
