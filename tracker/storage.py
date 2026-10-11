import json
import os
import tempfile
import threading
import uuid
from datetime import date
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Reentrant for nested load/save calls inside one read/modify/write cycle.
_LOCK = threading.RLock()
_LOCAL = threading.local()


class InvalidNumericData(ValueError):
    """JSON must never persist NaN or infinity as financial values."""


@contextmanager
def transaction():
    """Serialize an entire data operation, across threads AND server processes.

    HTTP requests and startup migrations use this automatically. Scripts that
    read, modify and save must enclose the complete cycle in this context.
    The lock file is stable: never unlink it while another process may use it.
    """
    with _LOCK:
        if getattr(_LOCAL, "depth", 0):
            _LOCAL.depth += 1
            try:
                yield
            finally:
                _LOCAL.depth -= 1
            return
        directory = os.path.dirname(FILES["projects"])
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, ".storage.lock"), "a+b") as lock_file:
            if os.name == "nt":
                import errno
                import msvcrt
                import time
                if os.fstat(lock_file.fileno()).st_size == 0:
                    lock_file.write(b"\0")
                    lock_file.flush()
                lock_file.seek(0)
                # LK_LOCK gives up after ten seconds; a legitimate long PDF
                # must not cause another request to fail while waiting.
                while True:
                    try:
                        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                        break
                    except OSError as error:
                        if error.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                            raise
                        time.sleep(.05)
            else:
                import fcntl
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            _LOCAL.depth = 1
            _LOCAL.pending = {}
            try:
                yield
                for path, encoded in _LOCAL.pending.items():
                    _write_atomic(path, encoded)
            finally:
                _LOCAL.depth = 0
                _LOCAL.pending = {}
                if os.name == "nt":
                    lock_file.seek(0)
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

FILES = {
    "projects": os.path.join(DATA_DIR, "projects.json"),
    "tasks": os.path.join(DATA_DIR, "tasks.json"),
    "deliveries": os.path.join(DATA_DIR, "deliveries.json"),
    "quotes": os.path.join(DATA_DIR, "quotes.json"),
    "materiales": os.path.join(DATA_DIR, "materiales.json"),
    "fichas": os.path.join(DATA_DIR, "fichas.json"),
    "catalogo": os.path.join(DATA_DIR, "catalogo.json"),
    "proveedores": os.path.join(DATA_DIR, "proveedores.json"),
    "team": os.path.join(DATA_DIR, "team.json"),
    "bundles": os.path.join(DATA_DIR, "bundles.json"),
    "comparison_rules": os.path.join(DATA_DIR, "comparison_rules.json"),
    "comparison_ignored_items": os.path.join(DATA_DIR, "comparison_ignored_items.json"),
    "company":           os.path.join(DATA_DIR, "company.json"),
    "project_templates": os.path.join(DATA_DIR, "project_templates.json"),
    "quote_templates":   os.path.join(DATA_DIR, "quote_templates.json"),
    "terms_templates":   os.path.join(DATA_DIR, "terms_templates.json"),
    "alcances":          os.path.join(DATA_DIR, "alcances.json"),
    "disciplinas":       os.path.join(DATA_DIR, "disciplinas.json"),
    "payments":          os.path.join(DATA_DIR, "payments.json"),
    "quote_status_labels": os.path.join(DATA_DIR, "quote_status_labels.json"),
}


def load(key):
    with transaction():
        pending = _LOCAL.pending.get(FILES[key])
        if pending is not None:
            return json.loads(pending)
        try:
            with open(FILES[key], "r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError:
            return []


def save(key, data):
    path = FILES[key]
    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)
    with transaction():
        # Validate before touching the existing file or allocating a temp file.
        try:
            encoded = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)
        except ValueError as error:
            raise InvalidNumericData(str(error)) from error
        _LOCAL.pending[path] = encoded


def _write_atomic(path, encoded):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=os.path.dirname(path), delete=False, suffix=".tmp"
        ) as tmp:
            tmp_path = tmp.name
            tmp.write(encoded)
        os.replace(tmp_path, path)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def new_id():
    return str(uuid.uuid4())[:8].upper()


def today():
    return date.today().isoformat()
