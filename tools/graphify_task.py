#!/usr/bin/env python3

import sys


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    action = argv[0] if argv else "update"
    if action in {"update", "check-update"}:
        print("[graphify] shim local en PATH; no hay binario graphify real disponible, se omite la actualizacion local.")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
