# save()

> God node · 74 connections · [/Users/macbook/ProjectTracker/tracker/storage.py](file:///Users/macbook/ProjectTracker/tracker/storage.py#L46)

## Call Trace Diagram

```mermaid
sequenceDiagram
    participant P0 as save()
    participant P1 as import_ldm_csv_upload()
    participant P2 as load()
    participant P3 as catalog_maps()
    participant P4 as build_project_detail_context()
    participant P5 as ._get_project()
    participant P6 as _find_project()
    participant P7 as sync_ldm_bundles()
    participant P8 as import_ldm_pdf_create()
    participant P9 as add_bundle_version_route()
    participant P10 as new_ldm()
    participant P11 as bundles()
    participant P12 as export_data()
    participant P13 as new_quote()
    participant P14 as quote_pdf_editor()
    participant P15 as edit_ldm()
    participant P16 as import_ldm_pdf_map()
    participant P17 as catalogo()
    participant P18 as update_bundle_version()
    participant P19 as import_quote_csv()
    participant P20 as mobile_generate_pdf()
    participant P21 as _bundle_suggestion_ldm()
    participant P22 as proveedores()
    participant P23 as fichas()
    participant P24 as team()
    participant P25 as edit_quote()
    participant P26 as _load_company()
    participant P27 as _load_pdf_import()
    participant P28 as update_bundle()
    participant P29 as purge_deleted_item()
    participant P30 as new_project()
    participant P31 as mobile_items()
    participant P32 as main()
    participant P33 as _migrate_quote_approval()
    participant P34 as _render_ldm_form()
    participant P35 as _bundle_sync_suggestions()
    participant P36 as ldm_pdf()
    participant P37 as _render_catalogo()
    participant P38 as _render_proveedores()
    participant P39 as activate_bundle_version_route()
    participant P40 as delete_bundle_version_route()
    participant P41 as empresa_logo()
    participant P42 as purge_quote_deleted_catalog_items()
    participant P43 as update_stage_budget()
    participant P44 as _find_project()
    participant P45 as mobile_add_item()
    participant P46 as migrate_catalog_fields()
    participant P47 as migrate_catalog_disciplina()
    participant P48 as catalog_description_lookup()
    participant P49 as get_alcances()
    participant P50 as purge_ldm_deleted_catalog_items()
    participant P51 as _render_fichas()
    participant P52 as edit_catalogo()
    participant P53 as api_catalogo_add()
    participant P54 as _render_bundles()
    participant P55 as approve_quote_route()
    participant P56 as quote_pdf()
    participant P57 as quote_excel()
    participant P58 as restore_deleted_item()
    participant P59 as preserve_deleted_item()
    participant P60 as quote_resumen_excel()
    participant P61 as quote_duplicate()
    participant P62 as add_doc_checklist()
    participant P63 as .setUp()
    participant P64 as .test_update_stage_budget_skips_without_template()
    participant P65 as _csv_already_imported()
    participant P66 as ldm_csv()
    participant P67 as delete_ldm()
    participant P68 as set_ldm_cot()
    participant P69 as _render_team()
    participant P70 as delete_catalogo()
    participant P71 as migrate_catalog_marca()
    participant P72 as bulk_delete_catalogo()
    participant P73 as api_catalogo_categorias()
    participant P74 as _catalog_by_id()
    participant P75 as edit_proveedor()
    participant P76 as _find_project()
    participant P77 as view_quote()
    participant P78 as quote_resumen_pdf()
    participant P79 as quote_csv_export()
    participant P80 as audit_deleted_catalog()
    participant P81 as _find_project()
    participant P82 as update_project()
    participant P83 as update_project_status()
    participant P84 as close_project()
    participant P85 as delete_project()
    participant P86 as update_stage_status()
    participant P87 as toggle_doc_checklist()
    participant P88 as delete_doc_checklist()
    participant P89 as mobile_remove_item()
    participant P90 as mobile_review()
    participant P91 as .test_upload_stores_pdf_import_payload_outside_cookie_session()
    participant P92 as get_disciplinas()
    participant P93 as get_progress()
    participant P94 as api_ldm_set_costo()
    participant P95 as bulk_edit_catalogo()
    participant P96 as api_catalogo()
    participant P97 as _catalog_sorted_by_name()
    participant P98 as delete_bundle()
    participant P99 as delete_proveedor()
    participant P100 as link_ficha()
    participant P101 as unlink_ficha()
    participant P102 as delete_ficha()
    participant P103 as delete_member()
    participant P104 as delete_quote()
    participant P105 as quote_resumen()
    participant P106 as all_quotes()
    participant P107 as dashboard()
    participant P108 as reopen_project()
    participant P109 as delete_delivery()
    participant P110 as api_catalogo_impact()
    participant P111 as mobile_projects()
    participant P112 as today()
    participant P113 as parse_ldm_csv()
    participant P114 as new_id()
    participant P115 as validate_csv_catalog_items()
    participant P116 as validate_ldm_form()
    participant P117 as ldm_from_form()
    participant P118 as parse_csv_plano_filename()
    participant P119 as _hydrate_import_items()
    participant P120 as _flash_csv_catalog_errors()
    participant P121 as import_ldm_pdf_upload()
    participant P122 as _build_export_like_xlsx()
    participant P123 as .tearDown()
    participant P124 as import_json()
    participant P125 as alcances_api_save()
    participant P126 as disciplinas_api_save()
    P0->>+ P1: calls
    P1-->>- P0: return
    P1->>+ P2: calls
    P2-->>- P1: return
    P2->>+ P3: calls
    P3-->>- P2: return
    P2->>+ P4: calls
    P4-->>- P2: return
    P2->>+ P1: calls
    P1-->>- P2: return
    P2->>+ P5: calls
    P5-->>- P2: return
    P2->>+ P6: calls
    P6-->>- P2: return
    P2->>+ P7: calls
    P7-->>- P2: return
    P2->>+ P8: calls
    P8-->>- P2: return
    P2->>+ P9: calls
    P9-->>- P2: return
    P2->>+ P10: calls
    P10-->>- P2: return
    P2->>+ P11: calls
    P11-->>- P2: return
    P2->>+ P12: calls
    P12-->>- P2: return
    P2->>+ P13: calls
    P13-->>- P2: return
    P2->>+ P14: calls
    P14-->>- P2: return
    P2->>+ P15: calls
    P15-->>- P2: return
    P2->>+ P16: calls
    P16-->>- P2: return
    P2->>+ P17: calls
    P17-->>- P2: return
    P2->>+ P18: calls
    P18-->>- P2: return
    P2->>+ P19: calls
    P19-->>- P2: return
    P2->>+ P20: calls
    P20-->>- P2: return
    P2->>+ P21: calls
    P21-->>- P2: return
    P2->>+ P22: calls
    P22-->>- P2: return
    P2->>+ P23: calls
    P23-->>- P2: return
    P2->>+ P24: calls
    P24-->>- P2: return
    P2->>+ P25: calls
    P25-->>- P2: return
    P2->>+ P26: calls
    P26-->>- P2: return
    P2->>+ P27: calls
    P27-->>- P2: return
    P2->>+ P28: calls
    P28-->>- P2: return
    P2->>+ P29: calls
    P29-->>- P2: return
    P2->>+ P30: calls
    P30-->>- P2: return
    P2->>+ P31: calls
    P31-->>- P2: return
    P2->>+ P32: calls
    P32-->>- P2: return
    P2->>+ P33: calls
    P33-->>- P2: return
    P2->>+ P34: calls
    P34-->>- P2: return
    P2->>+ P35: calls
    P35-->>- P2: return
    P2->>+ P36: calls
    P36-->>- P2: return
    P2->>+ P37: calls
    P37-->>- P2: return
    P2->>+ P38: calls
    P38-->>- P2: return
    P2->>+ P39: calls
    P39-->>- P2: return
    P2->>+ P40: calls
    P40-->>- P2: return
    P2->>+ P41: calls
    P41-->>- P2: return
    P2->>+ P42: calls
    P42-->>- P2: return
    P2->>+ P43: calls
    P43-->>- P2: return
    P2->>+ P44: calls
    P44-->>- P2: return
    P2->>+ P45: calls
    P45-->>- P2: return
    P2->>+ P46: calls
    P46-->>- P2: return
    P2->>+ P47: calls
    P47-->>- P2: return
    P2->>+ P48: calls
    P48-->>- P2: return
    P2->>+ P49: calls
    P49-->>- P2: return
    P2->>+ P50: calls
    P50-->>- P2: return
    P2->>+ P51: calls
    P51-->>- P2: return
    P2->>+ P52: calls
    P52-->>- P2: return
    P2->>+ P53: calls
    P53-->>- P2: return
    P2->>+ P54: calls
    P54-->>- P2: return
    P2->>+ P55: calls
    P55-->>- P2: return
    P2->>+ P56: calls
    P56-->>- P2: return
    P2->>+ P57: calls
    P57-->>- P2: return
    P2->>+ P58: calls
    P58-->>- P2: return
    P2->>+ P59: calls
    P59-->>- P2: return
    P2->>+ P60: calls
    P60-->>- P2: return
    P2->>+ P61: calls
    P61-->>- P2: return
    P2->>+ P62: calls
    P62-->>- P2: return
    P2->>+ P63: calls
    P63-->>- P2: return
    P2->>+ P64: calls
    P64-->>- P2: return
    P2->>+ P65: calls
    P65-->>- P2: return
    P2->>+ P66: calls
    P66-->>- P2: return
    P2->>+ P67: calls
    P67-->>- P2: return
    P2->>+ P68: calls
    P68-->>- P2: return
    P2->>+ P69: calls
    P69-->>- P2: return
    P2->>+ P70: calls
    P70-->>- P2: return
    P2->>+ P71: calls
    P71-->>- P2: return
    P2->>+ P72: calls
    P72-->>- P2: return
    P2->>+ P73: calls
    P73-->>- P2: return
    P2->>+ P74: calls
    P74-->>- P2: return
    P2->>+ P75: calls
    P75-->>- P2: return
    P2->>+ P76: calls
    P76-->>- P2: return
    P2->>+ P77: calls
    P77-->>- P2: return
    P2->>+ P78: calls
    P78-->>- P2: return
    P2->>+ P79: calls
    P79-->>- P2: return
    P2->>+ P80: calls
    P80-->>- P2: return
    P2->>+ P81: calls
    P81-->>- P2: return
    P2->>+ P82: calls
    P82-->>- P2: return
    P2->>+ P83: calls
    P83-->>- P2: return
    P2->>+ P84: calls
    P84-->>- P2: return
    P2->>+ P85: calls
    P85-->>- P2: return
    P2->>+ P86: calls
    P86-->>- P2: return
    P2->>+ P87: calls
    P87-->>- P2: return
    P2->>+ P88: calls
    P88-->>- P2: return
    P2->>+ P89: calls
    P89-->>- P2: return
    P2->>+ P90: calls
    P90-->>- P2: return
    P2->>+ P91: calls
    P91-->>- P2: return
    P2->>+ P92: calls
    P92-->>- P2: return
    P2->>+ P93: calls
    P93-->>- P2: return
    P2->>+ P94: calls
    P94-->>- P2: return
    P2->>+ P95: calls
    P95-->>- P2: return
    P2->>+ P96: calls
    P96-->>- P2: return
    P2->>+ P97: calls
    P97-->>- P2: return
    P2->>+ P98: calls
    P98-->>- P2: return
    P2->>+ P99: calls
    P99-->>- P2: return
    P2->>+ P100: calls
    P100-->>- P2: return
    P2->>+ P101: calls
    P101-->>- P2: return
    P2->>+ P102: calls
    P102-->>- P2: return
    P2->>+ P103: calls
    P103-->>- P2: return
    P2->>+ P104: calls
    P104-->>- P2: return
    P2->>+ P105: calls
    P105-->>- P2: return
    P2->>+ P106: calls
    P106-->>- P2: return
    P2->>+ P107: calls
    P107-->>- P2: return
    P2->>+ P108: calls
    P108-->>- P2: return
    P2->>+ P109: calls
    P109-->>- P2: return
    P2->>+ P110: calls
    P110-->>- P2: return
    P2->>+ P111: calls
    P111-->>- P2: return
    P1->>+ P0: calls
    P0-->>- P1: return
    P1->>+ P112: calls
    P112-->>- P1: return
    P1->>+ P113: calls
    P113-->>- P1: return
    P1->>+ P114: calls
    P114-->>- P1: return
    P1->>+ P115: calls
    P115-->>- P1: return
    P1->>+ P6: calls
    P6-->>- P1: return
    P1->>+ P116: calls
    P116-->>- P1: return
    P1->>+ P34: calls
    P34-->>- P1: return
    P1->>+ P117: calls
    P117-->>- P1: return
    P1->>+ P118: calls
    P118-->>- P1: return
    P1->>+ P65: calls
    P65-->>- P1: return
    P1->>+ P119: calls
    P119-->>- P1: return
    P1->>+ P120: calls
    P120-->>- P1: return
    P0->>+ P7: calls
    P7-->>- P0: return
    P0->>+ P8: calls
    P8-->>- P0: return
    P0->>+ P9: calls
    P9-->>- P0: return
    P0->>+ P10: calls
    P10-->>- P0: return
    P0->>+ P11: calls
    P11-->>- P0: return
    P0->>+ P12: calls
    P12-->>- P0: return
    P0->>+ P13: calls
    P13-->>- P0: return
    P0->>+ P14: calls
    P14-->>- P0: return
    P0->>+ P15: calls
    P15-->>- P0: return
    P0->>+ P17: calls
    P17-->>- P0: return
    P0->>+ P18: calls
    P18-->>- P0: return
    P0->>+ P19: calls
    P19-->>- P0: return
    P0->>+ P20: calls
    P20-->>- P0: return
    P0->>+ P22: calls
    P22-->>- P0: return
    P0->>+ P23: calls
    P23-->>- P0: return
    P0->>+ P24: calls
    P24-->>- P0: return
    P0->>+ P25: calls
    P25-->>- P0: return
    P0->>+ P121: calls
    P121-->>- P0: return
    P0->>+ P28: calls
    P28-->>- P0: return
    P0->>+ P29: calls
    P29-->>- P0: return
    P0->>+ P30: calls
    P30-->>- P0: return
    P0->>+ P31: calls
    P31-->>- P0: return
    P0->>+ P33: calls
    P33-->>- P0: return
    P0->>+ P39: calls
    P39-->>- P0: return
    P0->>+ P40: calls
    P40-->>- P0: return
    P0->>+ P42: calls
    P42-->>- P0: return
    P0->>+ P43: calls
    P43-->>- P0: return
    P0->>+ P45: calls
    P45-->>- P0: return
    P0->>+ P122: calls
    P122-->>- P0: return
    P0->>+ P46: calls
    P46-->>- P0: return
    P0->>+ P47: calls
    P47-->>- P0: return
    P0->>+ P50: calls
    P50-->>- P0: return
    P0->>+ P52: calls
    P52-->>- P0: return
    P0->>+ P53: calls
    P53-->>- P0: return
    P0->>+ P55: calls
    P55-->>- P0: return
    P0->>+ P57: calls
    P57-->>- P0: return
    P0->>+ P58: calls
    P58-->>- P0: return
    P0->>+ P59: calls
    P59-->>- P0: return
    P0->>+ P60: calls
    P60-->>- P0: return
    P0->>+ P61: calls
    P61-->>- P0: return
    P0->>+ P62: calls
    P62-->>- P0: return
    P0->>+ P63: calls
    P63-->>- P0: return
    P0->>+ P64: calls
    P64-->>- P0: return
    P0->>+ P67: calls
    P67-->>- P0: return
    P0->>+ P68: calls
    P68-->>- P0: return
    P0->>+ P70: calls
    P70-->>- P0: return
    P0->>+ P71: calls
    P71-->>- P0: return
    P0->>+ P72: calls
    P72-->>- P0: return
    P0->>+ P75: calls
    P75-->>- P0: return
    P0->>+ P82: calls
    P82-->>- P0: return
    P0->>+ P83: calls
    P83-->>- P0: return
    P0->>+ P84: calls
    P84-->>- P0: return
    P0->>+ P85: calls
    P85-->>- P0: return
    P0->>+ P86: calls
    P86-->>- P0: return
    P0->>+ P87: calls
    P87-->>- P0: return
    P0->>+ P88: calls
    P88-->>- P0: return
    P0->>+ P89: calls
    P89-->>- P0: return
    P0->>+ P94: calls
    P94-->>- P0: return
    P0->>+ P95: calls
    P95-->>- P0: return
    P0->>+ P98: calls
    P98-->>- P0: return
    P0->>+ P99: calls
    P99-->>- P0: return
    P0->>+ P100: calls
    P100-->>- P0: return
    P0->>+ P101: calls
    P101-->>- P0: return
    P0->>+ P102: calls
    P102-->>- P0: return
    P0->>+ P103: calls
    P103-->>- P0: return
    P0->>+ P104: calls
    P104-->>- P0: return
    P0->>+ P108: calls
    P108-->>- P0: return
    P0->>+ P109: calls
    P109-->>- P0: return
    P0->>+ P123: calls
    P123-->>- P0: return
    P0->>+ P124: calls
    P124-->>- P0: return
    P0->>+ P125: calls
    P125-->>- P0: return
    P0->>+ P126: calls
    P126-->>- P0: return
```

## Connections by Relation

### calls
- [[import_ldm_csv_upload()]] `INFERRED`
- [[sync_ldm_bundles()]] `INFERRED`
- [[import_ldm_pdf_create()]] `INFERRED`
- [[add_bundle_version_route()]] `INFERRED`
- [[new_ldm()]] `INFERRED`
- [[bundles()]] `INFERRED`
- [[export_data()]] `INFERRED`
- [[new_quote()]] `INFERRED`
- [[quote_pdf_editor()]] `INFERRED`
- [[edit_ldm()]] `INFERRED`
- [[catalogo()]] `INFERRED`
- [[update_bundle_version()]] `INFERRED`
- [[import_quote_csv()]] `INFERRED`
- [[mobile_generate_pdf()]] `INFERRED`
- [[proveedores()]] `INFERRED`
- [[fichas()]] `INFERRED`
- [[team()]] `INFERRED`
- [[edit_quote()]] `INFERRED`
- [[import_ldm_pdf_upload()]] `INFERRED`
- [[update_bundle()]] `INFERRED`

### contains
- [[storage.py]] `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*