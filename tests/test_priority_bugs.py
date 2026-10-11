"""P1 regressions use only temporary JSON files and an isolated auth database."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from flask import template_rendered
from werkzeug.datastructures import MultiDict

import tracker
from tracker import auth, storage
from tracker.validators import validate_quote_form, validate_ldm_form


PROJECT = {"id": "P1", "name": "Alfa", "clave": "ALFA", "client": "Cliente",
           "folder_num": "001", "version": "V1", "status": "Activo", "closed_at": None,
           "alcances": [], "template_id": "residencial"}
QUOTE = {"id": "Q1", "project_id": "P1", "quote_type": "Proyecto", "quote_number": "COT-ALFA-01",
         "date": "2026-10-11", "currency": "MXN", "tax_rate": 0, "discount_pct": 0,
         "approval_status": "active", "cover_discipline": "Nombre original",
         "items": [{"catalog_item_id": "CAT1", "description": "Artículo", "unit": "pza",
                    "qty": 10, "price": 10, "total": 100}], "specs": {"terms": []},
         "subtotal": 100, "total": 100, "created_at": "2026-10-11"}
LDM = {"id": "L1", "project_id": "P1", "ldm_number": "LDM-01", "proveedor": "Proveedor",
       "fecha": "2026-10-11", "items": [], "subtotal_cot": 0}


class IsolatedAppFixture(unittest.TestCase):
    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.root = self.stack.enter_context(tempfile.TemporaryDirectory(prefix="tracker-p1-"))
        self.stack.enter_context(patch.dict(storage.FILES, {key: str(Path(self.root) / (key + ".json"))
                                                           for key in storage.FILES}))
        for module in (tracker, auth):
            self.stack.enter_context(patch.object(module, "DATA_DIR", self.root))
        self.stack.enter_context(patch.object(auth, "AUTH_DB", str(Path(self.root) / "auth.db")))
        self.stack.enter_context(patch.dict(os.environ, {"PROJECT_TRACKER_ADMIN_PASSWORD": "Synthetic-admin-only",
                                                        "PROJECT_TRACKER_ADMIN_USERNAME": "admin",
                                                        "PROJECT_TRACKER_ADMIN_RESET": "0"}))
        with contextlib.redirect_stdout(io.StringIO()):
            self.app = tracker.create_app()
        self.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, LOGIN_DISABLED=False)
        @self.app.post("/test/invalid-finance")
        def invalid_finance():
            storage.save("quotes", [])
            storage.save("materiales", [{"subtotal_cot": float("nan")}])
            return "ok"
        for key in storage.FILES:
            storage.save(key, [])
        storage.save("projects", [copy.deepcopy(PROJECT), {**PROJECT, "id": "P2", "name": "Beta"}])
        storage.save("quotes", [copy.deepcopy(QUOTE)])
        storage.save("materiales", [copy.deepcopy(LDM)])
        storage.save("catalogo", [{"id": "CAT1", "nombre": "Artículo", "unidad": "pza", "precio": 10}])
        storage.save("company", {"name": "Empresa de prueba"})
        auth.create_user("cotizador", "Synthetic-user-only")
        self.uid = auth.get_user_by_username("cotizador")["id"]
        self.client = self.app.test_client()
        self.login()

    def login(self, admin=False):
        self.client.post("/logout")
        self.client.post("/login", data={"username": "admin" if admin else "cotizador",
                                        "password": "Synthetic-admin-only" if admin else "Synthetic-user-only"})

    def grant(self, **overrides):
        auth.set_user_permissions(self.uid, {**{key: True for key in auth.KNOWN_PERMISSIONS}, **overrides})

    def snapshot(self):
        return {key: storage.load(key) for key in storage.FILES}


class IsolatedPriorityTests(IsolatedAppFixture):

    def test_terms_script_and_both_editors_are_available(self):
        self.grant()
        response = self.client.get("/static/quote_terms_editor.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"function addTerm", response.data)
        for url in ("/projects/P1/quote/Q1/edit", "/projects/P1/quote/Q1/pdf-editor"):
            page = self.client.get(url)
            self.assertEqual(page.status_code, 200)
            self.assertIn(b'/static/quote_terms_editor.js', page.data)

    def test_only_admin_can_delete_project_even_with_all_permissions(self):
        self.grant()
        before = self.snapshot()
        self.assertEqual(self.client.post("/projects/P1/delete").status_code, 302)
        self.assertEqual(self.snapshot(), before)
        self.login(admin=True)
        self.assertEqual(self.client.post("/projects/P1/delete").status_code, 302)
        self.assertFalse(any(p["id"] == "P1" for p in storage.load("projects")))
        self.assertEqual(storage.load("quotes"), [])

    def test_no_grants_denies_read_and_write_without_changing_data(self):
        before = self.snapshot()
        self.assertEqual(self.client.get("/cotizaciones").status_code, 403)
        self.assertEqual(self.client.post("/projects/P1/quote/Q1/pdf-editor", data={"cover_discipline": "Intruso"}).status_code, 403)
        self.assertEqual(self.snapshot(), before)
        contexts = []
        def capture(sender, template, context, **kwargs):
            contexts.append(context)
        with template_rendered.connected_to(capture, self.app):
            page = self.client.get("/projects/P1")
        self.assertEqual(page.status_code, 200)
        self.assertEqual(contexts[-1]["quotes"], [])
        self.assertEqual(contexts[-1]["payments"], [])
        self.assertNotIn(b"COT-ALFA-01", page.data)

    def test_each_permission_is_enforced_individually(self):
        cases = [
            ("edit_projects", "POST", "/projects/P1/update", {"name": "Intruso"}),
            ("manage_tasks", "POST", "/projects/P1/docs-checklist/add", {"text": "Intruso"}),
            ("upload_files", "POST", "/projects/P1/quote/import", {}),
            ("download_files", "GET", "/projects/P1/quote/Q1/pdf", {}),
            ("view_quotes", "GET", "/projects/P1/quote/Q1/view", {}),
            ("edit_quotes", "POST", "/projects/P1/quote/Q1/pdf-editor", {"cover_discipline": "Intruso"}),
        ]
        for permission, method, url, data in cases:
            with self.subTest(permission=permission):
                self.grant(**{permission: False})
                before = self.snapshot()
                self.assertEqual(self.client.open(url, method=method, data=data).status_code, 403)
                self.assertEqual(self.snapshot(), before)
        self.grant(edit_quotes=False)
        self.assertEqual(self.client.get("/projects/P1/quote/Q1/view").status_code, 200)
        self.assertEqual(self.client.get("/projects/P1/quote/Q1/edit").status_code, 403)
        self.grant()
        self.client.post("/projects/P1/quote/Q1/pdf-editor", data={"cover_discipline": "Autorizado"})
        self.assertEqual(storage.load("quotes")[0]["cover_discipline"], "Autorizado")

    def test_import_cannot_bypass_quote_edit_permissions(self):
        self.grant(edit_quotes=False)
        before = self.snapshot()
        response = self.client.post("/import-json", data={"catalogo": (io.BytesIO(b"[]"), "catalogo.json")})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.snapshot(), before)

    def test_every_scoped_quote_and_ldm_route_checks_ownership(self):
        self.grant()
        checked = set()
        for rule in self.app.url_map.iter_rules():
            if not rule.endpoint.startswith(("quotes_bp.", "materials_bp.")):
                continue
            if "project_id" not in rule.arguments or not ({"quote_id", "ldm_id"} & rule.arguments):
                continue
            url = rule.rule.replace("<project_id>", "P2").replace("<quote_id>", "Q1").replace("<ldm_id>", "L1").replace("<int:item_index>", "0")
            for method in rule.methods - {"HEAD", "OPTIONS"}:
                with self.subTest(endpoint=rule.endpoint, method=method):
                    before = self.snapshot()
                    response = self.client.open(url, method=method, data={"cover_discipline": "Intruso", "project_name_override": "Intruso", "cot_proveedor": "on"})
                    self.assertEqual(response.status_code, 302)
                    self.assertEqual(self.snapshot(), before)
                    checked.add(rule.endpoint)
        self.assertGreaterEqual(len(checked), 25)
        self.client.post("/projects/P1/ldm/L1/editor", data={"project_name_override": "Autorizado"})
        self.assertEqual(storage.load("materiales")[0]["project_name_override"], "Autorizado")

    def test_payment_rejects_nonfinite_amounts_and_invalid_dates(self):
        self.grant()
        for amount in ("NaN", "Infinity", "-inf", "1e309", "0", "-1", "bad"):
            with self.subTest(amount=amount):
                self.client.post("/projects/P1/payments/add", data={"quote_id": "Q1", "date": "2026-10-11", "amount": amount})
                self.assertEqual(storage.load("payments"), [])
        for date in ("not-a-date", "2026-02-30", "2026-1-1", ""):
            with self.subTest(date=date):
                self.client.post("/projects/P1/payments/add", data={"quote_id": "Q1", "date": date, "amount": "10"})
                self.assertEqual(storage.load("payments"), [])
        self.client.post("/projects/P1/payments/add", data={"quote_id": "Q1", "date": "2026-10-11", "amount": "12,50"})
        self.assertEqual(storage.load("payments")[0]["amount"], 12.5)
        before = storage.load("payments")
        self.client.post(f'/projects/P1/payments/{before[0]["id"]}/edit', data={"date": "2026-10-11", "amount": "NaN"})
        self.assertEqual(storage.load("payments"), before)

    def test_quote_and_ldm_forms_reject_nonfinite_values(self):
        valid_quote = MultiDict({"date": "2026-10-11", "currency": "MXN", "item_desc[]": "Artículo",
                                 "item_unit[]": "pza", "item_qty[]": "2", "item_precio_costo[]": "10"})
        valid_ldm = MultiDict({"fecha": "2026-10-11", "proveedor": "Proveedor", "item_desc[]": "Artículo",
                               "item_unit[]": "pza", "item_qty[]": "2", "item_precio_cot[]": "10"})
        self.assertTrue(validate_quote_form(valid_quote, PROJECT)["ok"])
        self.assertTrue(validate_ldm_form(valid_ldm)["ok"])
        for raw in ("NaN", "inf", "-Infinity", "1e309"):
            for field in ("item_qty[]", "item_precio_costo[]", "item_pct_mo[]", "item_pct_indirectos[]",
                          "item_pct_utilidad[]", "discount_pct", "default_pct_mo"):
                with self.subTest(raw=raw, field=field):
                    quote_form = valid_quote.copy()
                    quote_form[field] = raw
                    self.assertFalse(validate_quote_form(quote_form, PROJECT)["ok"])
            for field in ("item_qty[]", "item_precio_cot[]"):
                ldm_form = valid_ldm.copy()
                ldm_form[field] = raw
                self.assertFalse(validate_ldm_form(ldm_form)["ok"])

    def test_failed_request_discards_pending_writes_and_releases_lock(self):
        self.grant()
        before = self.snapshot()
        self.assertEqual(self.client.post("/test/invalid-finance").status_code, 400)
        self.assertEqual(self.snapshot(), before)
        self.client.post("/projects/P1/quote/Q1/pdf-editor", data={"cover_discipline": "Guardado posterior"})
        self.assertEqual(storage.load("quotes")[0]["cover_discipline"], "Guardado posterior")

    def test_mobile_and_json_financial_apis_reject_nonfinite_values(self):
        self.grant()
        for raw in ("NaN", "inf", "1e309"):
            with self.subTest(raw=raw):
                before = self.snapshot()
                self.assertEqual(self.client.post("/api/catalogo/add", json={"nombre": "Malo", "precio": raw}).status_code, 400)
                self.assertEqual(self.client.post("/api/ldm/L1/costo", json={"subtotal_cot": raw}).status_code, 400)
                self.client.post("/cotizar/mobile/P1/items", data={"item_id": "CAT1", "qty": raw})
                self.assertEqual(self.snapshot(), before)


class StoragePriorityTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory(prefix="tracker-storage-")
        self.addCleanup(self.root.cleanup)
        self.files = {key: str(Path(self.root.name) / (key + ".json")) for key in storage.FILES}
        self.patch = patch.dict(storage.FILES, self.files)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        storage.save("quotes", [copy.deepcopy(QUOTE)])

    def test_transaction_preserves_two_concurrent_request_updates(self):
        # Use the same request hooks as the real application below instead of
        # testing separate load/save locks in isolation.
        with patch.object(tracker, "init_auth"), patch.object(tracker, "DATA_DIR", self.root.name), \
             patch.object(tracker, "migrate_catalog_fields"), patch.object(tracker, "migrate_catalog_disciplina"):
            app = tracker.create_app()
        app.config.update(TESTING=True, LOGIN_DISABLED=True, WTF_CSRF_ENABLED=False)
        first_loaded = threading.Event()
        release_first = threading.Event()
        second_started = threading.Event()
        results = []
        @app.post("/test/update/<field>")
        def update(field):
            quotes = storage.load("quotes")
            if field == "cover_discipline":
                first_loaded.set()
                if not release_first.wait(5):
                    raise TimeoutError("First update not released")
            quotes[0][field] = "Nombre A" if field == "cover_discipline" else "Nota B"
            storage.save("quotes", quotes)
            return "ok"
        def send(field):
            if field == "notes":
                second_started.set()
            with app.test_client() as client:
                results.append(client.post("/test/update/" + field).status_code)
        a = threading.Thread(target=send, args=("cover_discipline",))
        b = threading.Thread(target=send, args=("notes",))
        a.start()
        self.assertTrue(first_loaded.wait(5))
        b.start()
        self.assertTrue(second_started.wait(5))
        # Wait briefly so a broken per-call lock lets B load the stale snapshot.
        b.join(.15)
        release_first.set()
        a.join(5); b.join(5)
        self.assertFalse(a.is_alive() or b.is_alive())
        self.assertEqual(results, [200, 200])
        persisted = storage.load("quotes")[0]
        self.assertEqual(persisted["cover_discipline"], "Nombre A")
        self.assertEqual(persisted["notes"], "Nota B")

    def test_transaction_serializes_separate_server_processes(self):
        storage.save("quotes", [{"count": 0}])
        code = '''import json, sys, time
from tracker import storage
storage.FILES.update(json.loads(sys.argv[1]))
for _ in range(8):
    with storage.transaction():
        records = storage.load("quotes")
        time.sleep(.008)
        records[0]["count"] += 1
        storage.save("quotes", records)
'''
        children = [subprocess.Popen([sys.executable, "-c", code, json.dumps(self.files)], stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        for child in children:
            _, stderr = child.communicate(timeout=15)
            self.assertEqual(child.returncode, 0, stderr.decode())
        self.assertEqual(storage.load("quotes"), [{"count": 16}])

    def test_nonfinite_save_keeps_original_and_leaves_no_temp_file(self):
        before = Path(storage.FILES["quotes"]).read_bytes()
        for number in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(storage.InvalidNumericData):
                storage.save("quotes", [{"total": number}])
            self.assertEqual(Path(storage.FILES["quotes"]).read_bytes(), before)
        self.assertEqual(list(Path(self.root.name).glob("*.tmp")), [])

    def test_transaction_exception_discards_all_changes(self):
        before = storage.load("quotes")
        with self.assertRaises(ValueError):
            with storage.transaction():
                storage.save("quotes", [])
                with storage.transaction():
                    storage.save("materiales", [{"id": "pending"}])
                    self.assertEqual(storage.load("quotes"), [])
                raise ValueError("Abort synthetic operation")
        self.assertEqual(storage.load("quotes"), before)
        self.assertEqual(storage.load("materiales"), [])


class BootstrapPriorityTests(unittest.TestCase):
    def test_no_configuration_generates_unique_password_and_preserves_existing_account(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ, {}, clear=True), \
             patch.object(auth, "DATA_DIR", root), patch.object(auth, "AUTH_DB", str(Path(root) / "auth.db")), \
             patch.object(auth.secrets, "token_urlsafe", return_value="random-secret-one") as random_password, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(auth._default_admin_config(), ("admin", "", False))
            auth.init_db()
            random_password.assert_called_once_with(24)
            self.assertIsNotNone(auth.verify_credentials("admin", "random-secret-one"))
            auth.init_db()
            self.assertEqual(random_password.call_count, 1)
            self.assertIsNotNone(auth.verify_credentials("admin", "random-secret-one"))
            with patch.object(auth, "AUTH_DB", str(Path(root) / "other.db")), \
                 patch.object(auth.secrets, "token_urlsafe", return_value="random-secret-two"):
                auth.init_db()
                self.assertIsNotNone(auth.verify_credentials("admin", "random-secret-two"))
                self.assertIsNone(auth.verify_credentials("admin", "random-secret-one"))
