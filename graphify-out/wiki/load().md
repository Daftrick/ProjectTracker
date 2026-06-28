# load()

> God node · 114 connections · [/Users/macbook/ProjectTracker/tracker/storage.py](file:///Users/macbook/ProjectTracker/tracker/storage.py#L37)

## Call Trace Diagram

```mermaid
sequenceDiagram
    participant P0 as load()
    participant P1 as catalog_maps()
    participant P2 as catalog_name_key()
    participant P3 as parse_quote_csv()
    participant P4 as validate_csv_catalog_items()
    participant P5 as parse_quote_xlsx()
    participant P6 as catalog_description_lookup()
    participant P7 as resolve_catalog_binding()
    participant P8 as quote_catalog_description()
    participant P9 as _build_catalog_index()
    participant P10 as _match_catalog()
    participant P11 as _build_catalog_index()
    participant P12 as _match_catalog()
    participant P13 as _catalog_index()
    participant P14 as _csv_item_lookup()
    participant P15 as _attach_csv_item_metadata()
    participant P16 as sanitize_pdf_text()
    participant P17 as .test_catalog_name_key_normalizes_accents_and_special_separators()
    participant P18 as build_project_detail_context()
    participant P19 as _hydrate_quote_for_display()
    participant P20 as _render_quote_form()
    participant P21 as sync_ldm_bundles()
    participant P22 as import_ldm_pdf_create()
    participant P23 as quote_pdf_editor()
    participant P24 as export_data()
    participant P25 as mobile_generate_pdf()
    participant P26 as edit_ldm()
    participant P27 as import_ldm_pdf_map()
    participant P28 as _build_resumen()
    participant P29 as _bundle_suggestion_ldm()
    participant P30 as _quote_preview_from_csv()
    participant P31 as edit_quote()
    participant P32 as _build_quote_workbook()
    participant P33 as _parse_quote_items()
    participant P34 as _parse_ldm_items()
    participant P35 as purge_deleted_item()
    participant P36 as _hydrate_quote_for_display()
    participant P37 as purge_quote_deleted_catalog_items()
    participant P38 as _ldm_csv_response()
    participant P39 as ldm_pdf()
    participant P40 as mobile_add_item()
    participant P41 as quote_pdf()
    participant P42 as view_quote()
    participant P43 as quote_csv_export()
    participant P44 as _hydrate_import_items()
    participant P45 as import_ldm_csv_upload()
    participant P46 as ._get_project()
    participant P47 as _find_project()
    participant P48 as add_bundle_version_route()
    participant P49 as new_ldm()
    participant P50 as bundles()
    participant P51 as new_quote()
    participant P52 as catalogo()
    participant P53 as update_bundle_version()
    participant P54 as import_quote_csv()
    participant P55 as proveedores()
    participant P56 as fichas()
    participant P57 as team()
    participant P58 as _load_company()
    participant P59 as _load_pdf_import()
    participant P60 as update_bundle()
    participant P61 as new_project()
    participant P62 as mobile_items()
    participant P63 as main()
    participant P64 as _migrate_quote_approval()
    participant P65 as _render_ldm_form()
    participant P66 as _bundle_sync_suggestions()
    participant P67 as _render_catalogo()
    participant P68 as _render_proveedores()
    participant P69 as activate_bundle_version_route()
    participant P70 as delete_bundle_version_route()
    participant P71 as empresa_logo()
    participant P72 as update_stage_budget()
    participant P73 as _find_project()
    participant P74 as migrate_catalog_fields()
    participant P75 as migrate_catalog_disciplina()
    participant P76 as get_alcances()
    participant P77 as purge_ldm_deleted_catalog_items()
    participant P78 as _render_fichas()
    participant P79 as edit_catalogo()
    participant P80 as api_catalogo_add()
    participant P81 as _render_bundles()
    participant P82 as quote_templates()
    participant P83 as approve_quote_route()
    participant P84 as quote_excel()
    participant P85 as restore_deleted_item()
    participant P86 as preserve_deleted_item()
    participant P87 as quote_resumen_excel()
    participant P88 as quote_duplicate()
    participant P89 as add_doc_checklist()
    participant P90 as mobile_review()
    participant P91 as .setUp()
    participant P92 as .test_update_stage_budget_skips_without_template()
    participant P93 as _csv_already_imported()
    participant P94 as ldm_csv()
    participant P95 as delete_ldm()
    participant P96 as set_ldm_cot()
    participant P97 as _render_team()
    participant P98 as delete_catalogo()
    participant P99 as migrate_catalog_marca()
    participant P100 as bulk_delete_catalogo()
    participant P101 as api_catalogo_categorias()
    participant P102 as _catalog_by_id()
    participant P103 as edit_proveedor()
    participant P104 as _find_project()
    participant P105 as quote_resumen_pdf()
    participant P106 as audit_deleted_catalog()
    participant P107 as _find_project()
    participant P108 as update_project()
    participant P109 as update_project_status()
    participant P110 as close_project()
    participant P111 as delete_project()
    participant P112 as update_stage_status()
    participant P113 as toggle_doc_checklist()
    participant P114 as delete_doc_checklist()
    participant P115 as mobile_remove_item()
    participant P116 as .test_upload_stores_pdf_import_payload_outside_cookie_session()
    participant P117 as get_disciplinas()
    participant P118 as get_progress()
    participant P119 as api_ldm_set_costo()
    participant P120 as bulk_edit_catalogo()
    participant P121 as api_catalogo()
    participant P122 as _catalog_sorted_by_name()
    participant P123 as delete_bundle()
    participant P124 as delete_proveedor()
    participant P125 as link_ficha()
    participant P126 as unlink_ficha()
    participant P127 as delete_ficha()
    participant P128 as delete_member()
    participant P129 as delete_quote()
    participant P130 as quote_resumen()
    participant P131 as all_quotes()
    participant P132 as dashboard()
    participant P133 as reopen_project()
    participant P134 as delete_delivery()
    participant P135 as api_catalogo_impact()
    participant P136 as mobile_projects()
    P0->>+ P1: calls
    P1-->>- P0: return
    P1->>+ P0: calls
    P0-->>- P1: return
    P1->>+ P2: calls
    P2-->>- P1: return
    P2->>+ P1: calls
    P1-->>- P2: return
    P2->>+ P3: calls
    P3-->>- P2: return
    P2->>+ P4: calls
    P4-->>- P2: return
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
    P1->>+ P18: calls
    P18-->>- P1: return
    P1->>+ P19: calls
    P19-->>- P1: return
    P1->>+ P20: calls
    P20-->>- P1: return
    P1->>+ P21: calls
    P21-->>- P1: return
    P1->>+ P22: calls
    P22-->>- P1: return
    P1->>+ P23: calls
    P23-->>- P1: return
    P1->>+ P24: calls
    P24-->>- P1: return
    P1->>+ P25: calls
    P25-->>- P1: return
    P1->>+ P26: calls
    P26-->>- P1: return
    P1->>+ P27: calls
    P27-->>- P1: return
    P1->>+ P28: calls
    P28-->>- P1: return
    P1->>+ P29: calls
    P29-->>- P1: return
    P1->>+ P30: calls
    P30-->>- P1: return
    P1->>+ P31: calls
    P31-->>- P1: return
    P1->>+ P32: calls
    P32-->>- P1: return
    P1->>+ P33: calls
    P33-->>- P1: return
    P1->>+ P34: calls
    P34-->>- P1: return
    P1->>+ P35: calls
    P35-->>- P1: return
    P1->>+ P36: calls
    P36-->>- P1: return
    P1->>+ P37: calls
    P37-->>- P1: return
    P1->>+ P38: calls
    P38-->>- P1: return
    P1->>+ P39: calls
    P39-->>- P1: return
    P1->>+ P40: calls
    P40-->>- P1: return
    P1->>+ P41: calls
    P41-->>- P1: return
    P1->>+ P42: calls
    P42-->>- P1: return
    P1->>+ P43: calls
    P43-->>- P1: return
    P1->>+ P44: calls
    P44-->>- P1: return
    P0->>+ P18: calls
    P18-->>- P0: return
    P0->>+ P45: calls
    P45-->>- P0: return
    P0->>+ P46: calls
    P46-->>- P0: return
    P0->>+ P19: calls
    P19-->>- P0: return
    P0->>+ P47: calls
    P47-->>- P0: return
    P0->>+ P21: calls
    P21-->>- P0: return
    P0->>+ P22: calls
    P22-->>- P0: return
    P0->>+ P48: calls
    P48-->>- P0: return
    P0->>+ P23: calls
    P23-->>- P0: return
    P0->>+ P49: calls
    P49-->>- P0: return
    P0->>+ P50: calls
    P50-->>- P0: return
    P0->>+ P24: calls
    P24-->>- P0: return
    P0->>+ P51: calls
    P51-->>- P0: return
    P0->>+ P25: calls
    P25-->>- P0: return
    P0->>+ P26: calls
    P26-->>- P0: return
    P0->>+ P27: calls
    P27-->>- P0: return
    P0->>+ P52: calls
    P52-->>- P0: return
    P0->>+ P53: calls
    P53-->>- P0: return
    P0->>+ P54: calls
    P54-->>- P0: return
    P0->>+ P29: calls
    P29-->>- P0: return
    P0->>+ P55: calls
    P55-->>- P0: return
    P0->>+ P56: calls
    P56-->>- P0: return
    P0->>+ P57: calls
    P57-->>- P0: return
    P0->>+ P31: calls
    P31-->>- P0: return
    P0->>+ P58: calls
    P58-->>- P0: return
    P0->>+ P59: calls
    P59-->>- P0: return
    P0->>+ P60: calls
    P60-->>- P0: return
    P0->>+ P37: calls
    P37-->>- P0: return
    P0->>+ P35: calls
    P35-->>- P0: return
    P0->>+ P61: calls
    P61-->>- P0: return
    P0->>+ P36: calls
    P36-->>- P0: return
    P0->>+ P62: calls
    P62-->>- P0: return
    P0->>+ P63: calls
    P63-->>- P0: return
    P0->>+ P64: calls
    P64-->>- P0: return
    P0->>+ P65: calls
    P65-->>- P0: return
    P0->>+ P66: calls
    P66-->>- P0: return
    P0->>+ P39: calls
    P39-->>- P0: return
    P0->>+ P67: calls
    P67-->>- P0: return
    P0->>+ P68: calls
    P68-->>- P0: return
    P0->>+ P69: calls
    P69-->>- P0: return
    P0->>+ P70: calls
    P70-->>- P0: return
    P0->>+ P71: calls
    P71-->>- P0: return
    P0->>+ P41: calls
    P41-->>- P0: return
    P0->>+ P72: calls
    P72-->>- P0: return
    P0->>+ P73: calls
    P73-->>- P0: return
    P0->>+ P40: calls
    P40-->>- P0: return
    P0->>+ P74: calls
    P74-->>- P0: return
    P0->>+ P75: calls
    P75-->>- P0: return
    P0->>+ P6: calls
    P6-->>- P0: return
    P0->>+ P76: calls
    P76-->>- P0: return
    P0->>+ P77: calls
    P77-->>- P0: return
    P0->>+ P78: calls
    P78-->>- P0: return
    P0->>+ P79: calls
    P79-->>- P0: return
    P0->>+ P80: calls
    P80-->>- P0: return
    P0->>+ P81: calls
    P81-->>- P0: return
    P0->>+ P82: calls
    P82-->>- P0: return
    P0->>+ P42: calls
    P42-->>- P0: return
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
    P0->>+ P43: calls
    P43-->>- P0: return
    P0->>+ P88: calls
    P88-->>- P0: return
    P0->>+ P89: calls
    P89-->>- P0: return
    P0->>+ P90: calls
    P90-->>- P0: return
    P0->>+ P91: calls
    P91-->>- P0: return
    P0->>+ P92: calls
    P92-->>- P0: return
    P0->>+ P93: calls
    P93-->>- P0: return
    P0->>+ P94: calls
    P94-->>- P0: return
    P0->>+ P95: calls
    P95-->>- P0: return
    P0->>+ P96: calls
    P96-->>- P0: return
    P0->>+ P97: calls
    P97-->>- P0: return
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
    P0->>+ P105: calls
    P105-->>- P0: return
    P0->>+ P106: calls
    P106-->>- P0: return
    P0->>+ P107: calls
    P107-->>- P0: return
    P0->>+ P108: calls
    P108-->>- P0: return
    P0->>+ P109: calls
    P109-->>- P0: return
    P0->>+ P110: calls
    P110-->>- P0: return
    P0->>+ P111: calls
    P111-->>- P0: return
    P0->>+ P112: calls
    P112-->>- P0: return
    P0->>+ P113: calls
    P113-->>- P0: return
    P0->>+ P114: calls
    P114-->>- P0: return
    P0->>+ P115: calls
    P115-->>- P0: return
    P0->>+ P116: calls
    P116-->>- P0: return
    P0->>+ P117: calls
    P117-->>- P0: return
    P0->>+ P118: calls
    P118-->>- P0: return
    P0->>+ P119: calls
    P119-->>- P0: return
    P0->>+ P120: calls
    P120-->>- P0: return
    P0->>+ P121: calls
    P121-->>- P0: return
    P0->>+ P122: calls
    P122-->>- P0: return
    P0->>+ P123: calls
    P123-->>- P0: return
    P0->>+ P124: calls
    P124-->>- P0: return
    P0->>+ P125: calls
    P125-->>- P0: return
    P0->>+ P126: calls
    P126-->>- P0: return
    P0->>+ P127: calls
    P127-->>- P0: return
    P0->>+ P128: calls
    P128-->>- P0: return
    P0->>+ P129: calls
    P129-->>- P0: return
    P0->>+ P130: calls
    P130-->>- P0: return
    P0->>+ P131: calls
    P131-->>- P0: return
    P0->>+ P132: calls
    P132-->>- P0: return
    P0->>+ P133: calls
    P133-->>- P0: return
    P0->>+ P134: calls
    P134-->>- P0: return
    P0->>+ P135: calls
    P135-->>- P0: return
    P0->>+ P136: calls
    P136-->>- P0: return
```

## Connections by Relation

### calls
- [[catalog_maps()]] `INFERRED`
- [[build_project_detail_context()]] `INFERRED`
- [[import_ldm_csv_upload()]] `INFERRED`
- [[._get_project()]] `INFERRED`
- [[_hydrate_quote_for_display()]] `INFERRED`
- [[_find_project()]] `INFERRED`
- [[sync_ldm_bundles()]] `INFERRED`
- [[import_ldm_pdf_create()]] `INFERRED`
- [[add_bundle_version_route()]] `INFERRED`
- [[quote_pdf_editor()]] `INFERRED`
- [[new_ldm()]] `INFERRED`
- [[bundles()]] `INFERRED`
- [[export_data()]] `INFERRED`
- [[new_quote()]] `INFERRED`
- [[mobile_generate_pdf()]] `INFERRED`
- [[edit_ldm()]] `INFERRED`
- [[import_ldm_pdf_map()]] `INFERRED`
- [[catalogo()]] `INFERRED`
- [[update_bundle_version()]] `INFERRED`
- [[import_quote_csv()]] `INFERRED`

### contains
- [[storage.py]] `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*