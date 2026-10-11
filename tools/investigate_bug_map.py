"""Reproduce bugs with synthetic records and a temporary database only."""
import argparse
import contextlib
import copy
import io
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import unittest.mock as mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pdfplumber
from flask import template_rendered
from werkzeug.datastructures import MultiDict
import tracker
import tracker.auth as auth
import tracker.storage as storage
from tracker.pdfs import build_quote_pdf
from tracker.validators import validate_quote_form

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path(tempfile.gettempdir()) / 'projecttracker-investigate')
    parser.add_argument('--serve', action='store_true', help='Keep the synthetic app running on localhost for browser checks.')
    args = parser.parse_args()
    OUT = args.output_dir.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    PROJECT = {'id': 'P1', 'name': 'Proyecto Alfa', 'clave': 'ALFA', 'client': 'Cliente de prueba', 'folder_num': '001', 'version': 'V1', 'fecha': '261011', 'closed_at': None, 'status': 'Activo', 'alcances': [], 'template_id': 'residencial'}
    QUOTE = {'id': 'Q1', 'project_id': 'P1', 'quote_type': 'Proyecto', 'quote_number': 'COT-ALFA-P01-261011', 'version': 'V1', 'date': '2026-10-11', 'currency': 'MXN', 'tax_rate': 0, 'approval_status': 'active', 'cover_discipline': 'Diseño eléctrico', 'items': [{'catalog_item_id': 'CAT1', 'description': 'Artículo de prueba', 'unit': 'pza', 'qty': 10, 'price': 10, 'total': 100}], 'subtotal': 100, 'total': 100, 'tax': 0, 'specs': {'terms': []}, 'created_at': '2026-10-11'}
    LDM = {'id': 'L1', 'project_id': 'P1', 'ldm_number': 'LDM-ALFA-01', 'proveedor': 'Proveedor de prueba', 'fecha': '2026-10-11', 'subtotal_cot': 20, 'items': [{'catalog_item_id': 'CAT1', 'description': 'Artículo de prueba', 'unit': 'pza', 'qty': 10, 'precio_cot': 2, 'total_cot': 20}]}
    PAYMENT = {'id': 'PAY1', 'project_id': 'P1', 'quote_id': 'Q1', 'date': '2026-10-11', 'amount': 50, 'concept': 'Anticipo'}
    CATALOG = [{'id': 'CAT1', 'nombre': 'Artículo de prueba', 'descripcion': '', 'unidad': 'pza', 'precio': 10, 'categoria': '', 'disciplina': 'instalaciones'}]
    findings = []
    IDS = {'B14':'BUG-01', 'B03':'BUG-02', 'B01':'BUG-03', 'B04':'BUG-04', 'B08':'BUG-05', 'B13':'BUG-06', 'B06':'BUG-07', 'B05':'BUG-08', 'B07':'BUG-09', 'B09':'BUG-10', 'B12':'BUG-11', 'B10':'BUG-12', 'B11':'BUG-13'}

    def result(key, evidence):
        key = IDS[key]
        findings.append({'id': key, 'evidence': evidence})
        print(key, json.dumps(evidence, ensure_ascii=False))

    def seed():
        for key in storage.FILES:
            storage.save(key, [])
        storage.save('projects', [copy.deepcopy(PROJECT), {**PROJECT, 'id': 'P2', 'name': 'Proyecto Beta', 'clave': 'BETA', 'folder_num': '002'}])
        storage.save('quotes', [copy.deepcopy(QUOTE)])
        storage.save('materiales', [copy.deepcopy(LDM)])
        storage.save('catalogo', copy.deepcopy(CATALOG))
        storage.save('payments', [copy.deepcopy(PAYMENT)])
        storage.save('company', {'name': 'Empresa de prueba'})

    with tempfile.TemporaryDirectory(prefix='projecttracker-investigate-') as root, contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.dict(storage.FILES, {key: str(Path(root) / (key + '.json')) for key in storage.FILES}))
        stack.enter_context(mock.patch.object(tracker, 'DATA_DIR', root))
        stack.enter_context(mock.patch.object(auth, 'DATA_DIR', root))
        stack.enter_context(mock.patch.object(auth, 'AUTH_DB', str(Path(root) / 'auth.db')))
        stack.enter_context(mock.patch.dict(os.environ, {'PROJECT_TRACKER_ADMIN_USERNAME': 'audit-admin', 'PROJECT_TRACKER_ADMIN_PASSWORD': 'Synthetic-Audit-Password-Only', 'PROJECT_TRACKER_ADMIN_RESET': '0'}))
        with contextlib.redirect_stdout(io.StringIO()):
            app = tracker.create_app()
        app.config.update(TESTING=True, LOGIN_DISABLED=False, WTF_CSRF_ENABLED=False)
        seed()
        auth.create_user('audit-user', 'Synthetic-User-Password-Only', 'cotizador')
        uid = auth.get_user_by_username('audit-user')['id']
        client = app.test_client()
        assert client.post('/login', data={'username': 'audit-user', 'password': 'Synthetic-User-Password-Only'}).status_code == 302
        assert client.get('/usuarios').status_code == 302  # admin-only control works

        # Permissions disabled in the user record still allow reading and writing.
        assert auth.get_user_by_username('audit-user')['permissions'] == '{}'
        read = client.get('/cotizaciones')
        write = client.post('/projects/P1/quote/Q1/pdf-editor', data={'cover_discipline': 'Cambio sin permiso'})
        assert read.status_code == 200 and storage.load('quotes')[0]['cover_discipline'] == 'Cambio sin permiso'
        result('B01', {'permissions': {}, 'quotes_read_http': read.status_code, 'pdf_editor_post_http': write.status_code, 'name_changed': True})

        # Removing active access does not terminate an already authenticated session.
        auth.set_user_active(uid, False)
        existing_session = client.get('/cotizaciones')
        fresh = app.test_client()
        new_login = fresh.post('/login', data={'username': 'audit-user', 'password': 'Synthetic-User-Password-Only'})
        print('CONTROL inactive session:', existing_session.status_code, 'new login:', new_login.status_code)
        assert existing_session.status_code == 302 and new_login.status_code == 200
        auth.set_user_active(uid, True)
        client.post('/login', data={'username': 'audit-user', 'password': 'Synthetic-User-Password-Only'})

        seed()
        deletion = client.post('/projects/P1/delete')
        assert all(p['id'] != 'P1' for p in storage.load('projects'))
        result('B03', {'role': 'cotizador', 'delete_project_http': deletion.status_code, 'project_deleted': True})

        # Scope mismatch: contrast with guarded PDF editor.
        seed()
        guarded = client.get('/projects/P2/quote/Q1/pdf-editor')
        unguarded = client.get('/projects/P2/quote/Q1/edit')
        deleted = client.post('/projects/P2/quote/Q1/delete')
        assert guarded.status_code == 302 and unguarded.status_code == 200 and not storage.load('quotes')
        seed()
        ldm_write = client.post('/projects/P2/ldm/L1/editor', data={'project_name_override': 'Beta aplicado a Alfa'})
        assert storage.load('materiales')[0]['project_name_override'] == 'Beta aplicado a Alfa'
        ldm_delete = client.post('/projects/P2/ldm/L1/delete')
        assert not storage.load('materiales')
        result('B04', {'guarded_quote_pdf_editor_http': guarded.status_code, 'mismatched_quote_edit_http': unguarded.status_code, 'mismatched_quote_delete_http': deleted.status_code, 'quote_deleted': True, 'mismatched_ldm_write_http': ldm_write.status_code, 'mismatched_ldm_delete_http': ldm_delete.status_code, 'ldm_changed_and_deleted': True})

        seed()
        client.post('/projects/P1/quote/Q1/delete')
        assert storage.load('payments') and not storage.load('quotes')
        quote_orphans = len(storage.load('payments'))
        seed()
        client.post('/projects/P1/delete')
        assert storage.load('payments') and not any(p['id']=='P1' for p in storage.load('projects'))
        result('B05', {'payments_after_quote_delete': quote_orphans, 'payments_after_project_delete': len(storage.load('payments'))})

        seed()
        payment = client.post('/projects/P1/payments/add', data={'quote_id': 'Q1', 'date': 'not-a-date', 'amount': 'NaN'})
        values = storage.load('payments')
        assert math.isnan(values[-1]['amount']) and values[-1]['date'] == 'not-a-date'
        form = MultiDict({'quote_type': 'Proyecto', 'date': '2026-10-11', 'currency': 'MXN', 'item_desc[]': 'Artículo de prueba', 'item_unit[]': 'pza', 'item_qty[]': 'NaN', 'item_precio_costo[]': '10'})
        validation = validate_quote_form(form, PROJECT)
        assert validation['ok'] and math.isnan(validation['subtotal'])
        result('B06', {'payment_post_http': payment.status_code, 'nan_payment_persisted': True, 'invalid_payment_date_persisted': True, 'quote_validation_ok': validation['ok'], 'quote_subtotal_nan': True})

        seed()
        projects = storage.load('projects'); projects[0]['closed_at'] = '2026-10-11'; storage.save('projects', projects)
        client.post('/projects/P1/quote/Q1/pdf-editor', data={'cover_discipline': 'Cambia proyecto cerrado'})
        client.post('/cotizar/mobile/P1/items', data={'item_id': 'CAT1', 'qty': '1'})
        assert storage.load('quotes')[0]['cover_discipline'] == 'Cambia proyecto cerrado'
        assert any(q.get('status')=='draft' for q in storage.load('quotes'))
        result('B07', {'closed_project_pdf_name_changed': True, 'closed_project_mobile_draft_created': True})

        # Load and save each lock separately: reproduce a deterministic lost update.
        seed()
        first = storage.load('quotes'); second = storage.load('quotes')
        first[0]['cover_discipline'] = 'Nombre del editor A'; storage.save('quotes', first)
        second[0]['notes'] = 'Nota del editor B'; storage.save('quotes', second)
        persisted = storage.load('quotes')[0]
        assert persisted['cover_discipline'] == QUOTE['cover_discipline']
        result('B08', {'first_editor_name_lost': True, 'second_editor_note_saved': persisted['notes'] == 'Nota del editor B'})

        seed()
        contexts = []
        def capture(sender, template, context, **extra):
            contexts.append((template.name, context))
        qactive = copy.deepcopy(QUOTE)
        qdraft = {**copy.deepcopy(QUOTE), 'id': 'QD', 'approval_status': 'draft', 'total': 200, 'items': [{'description':'Borrador', 'unit':'pza', 'qty':1, 'price':200,'total':200}]}
        qold = {**copy.deepcopy(QUOTE), 'id': 'QO', 'approval_status': 'obsolete', 'total': 300, 'items': [{'description':'Obsoleta', 'unit':'pza', 'qty':1, 'price':300,'total':300}]}
        storage.save('quotes', [qactive, qdraft, qold])
        with template_rendered.connected_to(capture, app):
            assert client.get('/').status_code == 200
            assert client.get('/projects/P1').status_code == 200
        dashboard = next(ctx for tpl,ctx in contexts if tpl == 'dashboard.html')
        detail = next(ctx for tpl,ctx in contexts if tpl == 'project_detail.html')
        dashboard_total = next(p for p in dashboard['active'] if p['id']=='P1')['total_cotizado']
        assert dashboard_total == 600 and detail['total_cotizado'] == 100
        result('B09', {'dashboard_cotizado': dashboard_total, 'project_detail_cotizado': detail['total_cotizado']})

        # Numeric package size bypasses validation and raises instead of a form error.
        seed()
        try:
            client.post('/catalogo', data={'nombre': 'Rollo', 'precio': '10', 'buy_unit_size': '2,5'})
        except ValueError as exc:
            result('B10', {'catalog_decimal_comma_exception': type(exc).__name__, 'input': '2,5'})
        else:
            raise AssertionError('Expected catalog form ValueError was not reproduced')

        target = 'https://example.invalid/audit'
        fresh = app.test_client()
        response = fresh.post('/login?next=' + target, data={'username': 'audit-user', 'password': 'Synthetic-User-Password-Only'})
        assert response.headers['Location'] == target
        result('B11', {'login_redirects_to_external_url': True, 'http': response.status_code})

        # Normal cover: long description advances text into the fixed totals area.
        seed()
        q = copy.deepcopy(QUOTE)
        q['cover_discipline'] = ('Diseño integral de instalaciones eléctricas, iluminación y coordinación del proyecto ejecutivo para vivienda residencial. ' * 6).strip()
        q['specs']['portada_spacing'] = '40'
        with mock.patch('tracker.pdfs._load_company', return_value={'name':'Empresa de prueba'}), mock.patch('tracker.pdfs.quote_logo_path', return_value=None):
            pdf_bytes = build_quote_pdf(PROJECT, q)
        (OUT/'long-title.pdf').write_bytes(pdf_bytes)
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            words = pdf.pages[0].extract_words(extra_attrs=['size'])
            title_words = [w for w in words if abs(w['size']-24)<0.01]
            lower = max(w['bottom'] for w in title_words)
            totals_top = 221 * 72 / 25.4
            assert lower > totals_top
            result('B12', {'name_characters':len(q['cover_discipline']), 'title_bottom_mm':round(lower*25.4/72,2), 'summary_top_mm':221, 'title_overlaps_summary':True})

        # Known default admin password persists unless explicitly configured.
        with mock.patch.dict(os.environ, {}, clear=True):
            username, password, reset = auth._default_admin_config()
            with mock.patch.object(auth, 'AUTH_DB', str(Path(root) / 'default-auth.db')), contextlib.redirect_stdout(io.StringIO()):
                auth.init_db()
                default_user = auth.verify_credentials(username, password)
            assert default_user is not None and default_user.role == 'admin'
            result('B13', {'password_is_nonempty_without_environment_configuration':True, 'new_database_accepts_fixed_default_password':True, 'reset_requested':reset})

        assert (Path(storage.BASE_DIR)/'static'/'quote_terms_editor.js').is_file()
        static_response = client.get('/static/quote_terms_editor.js')
        assert static_response.status_code == 404
        result('B14', {'terms_javascript_http':static_response.status_code, 'file_exists_in_root_static':True, 'flask_static_folder_is_tracker_static':app.static_folder == str(Path(storage.BASE_DIR)/'tracker'/'static')})

        # Synthetic GET smoke checks for primary modules, still authenticated.
        seed()
        urls = ['/', '/kanban', '/projects/P1', '/projects/new', '/cotizaciones', '/pagos', '/projects/P1/quote/Q1/edit', '/projects/P1/quote/Q1/view', '/projects/P1/quote/Q1/pdf-editor', '/projects/P1/quote/Q1/pdf?inline=1', '/projects/P1/quote/Q1/excel', '/projects/P1/quote/Q1/csv', '/catalogo', '/bundles', '/proveedores', '/team', '/fichas', '/plantillas-cotizacion', '/cotizar/mobile/', '/cotizar/mobile/P1/items', '/projects/P1/ldm/L1/edit', '/projects/P1/ldm/L1/editor', '/projects/P1/ldm/L1/csv']
        smoke = {}
        for url in urls:
            response = client.get(url)
            smoke[url] = response.status_code
        assert all(status == 200 for status in smoke.values()), smoke
        print('SMOKE', json.dumps(smoke))
        (OUT/'smoke.json').write_text(json.dumps(smoke, indent=2))
        (OUT/'findings.json').write_text(json.dumps(findings, ensure_ascii=False, indent=2))
        if args.serve:
            app.config['WTF_CSRF_ENABLED'] = True
            app.run(host='127.0.0.1', port=5099, debug=False, use_reloader=False)

    (OUT/'findings.json').write_text(json.dumps(findings, ensure_ascii=False, indent=2))
    print('Confirmed findings:', len(findings))


if __name__ == "__main__":
    main()
