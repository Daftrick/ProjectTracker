"""Parse project Python files without writing bytecode."""

from __future__ import annotations

import ast
from pathlib import Path


ROOTS = (Path("app.py"), Path("tracker"), Path("tests"))


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for root in ROOTS:
        if root.is_dir():
            files.extend(sorted(root.rglob("*.py")))
        else:
            files.append(root)
    return files


def main() -> None:
    files = iter_python_files()
    for path in files:
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    print(f"Parsed {len(files)} Python files")


if __name__ == "__main__":
    main()
