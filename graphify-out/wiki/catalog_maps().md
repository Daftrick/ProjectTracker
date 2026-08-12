# catalog_maps()

> God node · 31 connections · [/Users/macbook/ProjectTracker/tracker/catalog.py](file:///Users/macbook/ProjectTracker/tracker/catalog.py#L180)

## Call Trace Diagram

```mermaid
sequenceDiagram
    participant P0 as catalog_maps()
    participant P1 as load()
    participant P2 as build_project_detail_context()
    participant P3 as today()
    participant P4 as hydrate_quote()
    participant P5 as compute_consistency()
    participant P6 as pick_active_quote()
    participant P7 as hydrate_ldm()
    participant P8 as is_base_quote_type()
    participant P9 as build_quote_row_views()
    participant P10 as get_quote_status_labels()
    participant P11 as build_consistency_view()
    participant P12 as payment_summary()
    participant P13 as get_payments_for_project()
    participant P14 as build_task_row_views()
    participant P15 as build_ldm_row_views()
    participant P16 as check_blocked()
    participant P17 as get_progress()
    participant P18 as project_detail()
    participant P19 as .test_context_totals_match_discounted_quote()
    participant P20 as .test_build_project_detail_context_groups_and_calculates_totals()
    participant P21 as .test_build_project_detail_context_sums_all_active_base_quotes()
    participant P22 as .test_build_project_detail_context_computes_total_pagado_and_saldo()
    participant P23 as .test_build_project_detail_context_saldo_can_go_negative_when_overpaid()
    participant P24 as import_ldm_csv_upload()
    participant P25 as ._get_project()
    participant P26 as _hydrate_quote_for_display()
    participant P27 as quote_pdf_editor()
    participant P28 as new_quote()
    participant P29 as mobile_generate_pdf()
    participant P30 as _find_project()
    participant P31 as sync_ldm_bundles()
    participant P32 as import_ldm_pdf_create()
    participant P33 as add_bundle_version_route()
    participant P34 as new_ldm()
    participant P35 as bundles()
    participant P36 as export_data()
    participant P37 as edit_quote()
    participant P38 as view_quote()
    participant P39 as edit_ldm()
    participant P40 as import_ldm_pdf_map()
    participant P41 as update_bundle_version()
    participant P42 as import_quote_csv()
    participant P43 as _bundle_suggestion_ldm()
    participant P44 as catalogo()
    participant P45 as _load_company()
    participant P46 as _load_pdf_import()
    participant P47 as update_bundle()
    participant P48 as proveedores()
    participant P49 as fichas()
    participant P50 as team()
    participant P51 as _fill_bundle_snapshots()
    participant P52 as purge_quote_deleted_catalog_items()
    participant P53 as purge_deleted_item()
    participant P54 as kanban()
    participant P55 as new_project()
    participant P56 as _hydrate_quote_for_display()
    participant P57 as mobile_items()
    participant P58 as main()
    participant P59 as ._status()
    participant P60 as _migrate_quote_approval()
    participant P61 as _render_ldm_form()
    participant P62 as _bundle_sync_suggestions()
    participant P63 as ldm_pdf()
    participant P64 as _render_catalogo()
    participant P65 as _render_proveedores()
    participant P66 as activate_bundle_version_route()
    participant P67 as delete_bundle_version_route()
    participant P68 as empresa_logo()
    participant P69 as quote_pdf()
    participant P70 as update_stage_budget()
    participant P71 as _find_project()
    participant P72 as mobile_add_item()
    participant P73 as migrate_catalog_fields()
    participant P74 as migrate_catalog_disciplina()
    participant P75 as catalog_description_lookup()
    participant P76 as get_alcances()
    participant P77 as purge_ldm_deleted_catalog_items()
    participant P78 as _render_fichas()
    participant P79 as edit_catalogo()
    participant P80 as api_catalogo_add()
    participant P81 as _render_bundles()
    participant P82 as approve_quote_route()
    participant P83 as set_quote_status_route()
    participant P84 as quote_excel()
    participant P85 as restore_deleted_item()
    participant P86 as preserve_deleted_item()
    participant P87 as quote_resumen_excel()
    participant P88 as quote_csv_export()
    participant P89 as quote_duplicate()
    participant P90 as quote_templates()
    participant P91 as add_doc_checklist()
    participant P92 as mobile_review()
    participant P93 as quote_templates()
    participant P94 as .setUp()
    participant P95 as .setUp()
    participant P96 as .setUp()
    participant P97 as .setUp()
    participant P98 as .test_update_stage_budget_skips_without_template()
    participant P99 as .setUp()
    participant P100 as .setUp()
    participant P101 as .setUp()
    participant P102 as .setUp()
    participant P103 as .test_override_survives_later_project_client_change()
    participant P104 as .setUp()
    participant P105 as .test_api_catalogo_add_accepts_multiline_nombre_and_descripcion()
    participant P106 as .setUp()
    participant P107 as .setUp()
    participant P108 as .setUp()
    participant P109 as _csv_already_imported()
    participant P110 as ldm_csv()
    participant P111 as delete_ldm()
    participant P112 as set_ldm_cot()
    participant P113 as _render_team()
    participant P114 as delete_catalogo()
    participant P115 as migrate_catalog_marca()
    participant P116 as bulk_delete_catalogo()
    participant P117 as api_catalogo_categorias()
    participant P118 as _catalog_by_id()
    participant P119 as edit_proveedor()
    participant P120 as _find_project()
    participant P121 as add_payment_route()
    participant P122 as quote_resumen_pdf()
    participant P123 as all_quotes()
    participant P124 as all_payments()
    participant P125 as audit_deleted_catalog()
    participant P126 as _find_project()
    participant P127 as toggle_obra()
    participant P128 as update_project()
    participant P129 as update_project_status()
    participant P130 as close_project()
    participant P131 as delete_project()
    participant P132 as update_stage_status()
    participant P133 as toggle_doc_checklist()
    participant P134 as delete_doc_checklist()
    participant P135 as mobile_remove_item()
    participant P136 as .test_closed_project_shows_readonly_badge_not_select()
    participant P137 as .test_payments_button_visible_even_for_closed_project()
    participant P138 as ._get_project()
    participant P139 as .test_upload_stores_pdf_import_payload_outside_cookie_session()
    participant P140 as .setUp()
    participant P141 as .test_new_quote_with_client_unchanged_has_no_override()
    participant P142 as .test_new_quote_with_edited_client_saves_override()
    participant P143 as .test_edit_quote_updates_proposal_for()
    participant P144 as .test_description_with_special_chars_is_escaped_as_text_content()
    participant P145 as .setUp()
    participant P146 as .setUp()
    participant P147 as get_disciplinas()
    participant P148 as api_ldm_set_costo()
    participant P149 as bulk_edit_catalogo()
    participant P150 as api_catalogo()
    participant P151 as _catalog_sorted_by_name()
    participant P152 as delete_bundle()
    participant P153 as delete_proveedor()
    participant P154 as link_ficha()
    participant P155 as unlink_ficha()
    participant P156 as delete_ficha()
    participant P157 as delete_member()
    participant P158 as delete_quote()
    participant P159 as quote_resumen()
    participant P160 as dashboard()
    participant P161 as reopen_project()
    participant P162 as delete_delivery()
    participant P163 as .test_multiline_description_round_trips_through_save()
    participant P164 as api_catalogo_impact()
    participant P165 as mobile_projects()
    participant P166 as catalog_name_key()
    participant P167 as _render_quote_form()
    participant P168 as _build_quote_workbook()
    participant P169 as _build_resumen()
    participant P170 as _quote_preview_from_csv()
    participant P171 as _parse_quote_items()
    participant P172 as _parse_ldm_items()
    participant P173 as _ldm_csv_response()
    participant P174 as _hydrate_import_items()
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
    P2->>+ P0: calls
    P0-->>- P2: return
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
    P1->>+ P45: calls
    P45-->>- P1: return
    P1->>+ P46: calls
    P46-->>- P1: return
    P1->>+ P47: calls
    P47-->>- P1: return
    P1->>+ P48: calls
    P48-->>- P1: return
    P1->>+ P49: calls
    P49-->>- P1: return
    P1->>+ P50: calls
    P50-->>- P1: return
    P1->>+ P51: calls
    P51-->>- P1: return
    P1->>+ P52: calls
    P52-->>- P1: return
    P1->>+ P53: calls
    P53-->>- P1: return
    P1->>+ P54: calls
    P54-->>- P1: return
    P1->>+ P55: calls
    P55-->>- P1: return
    P1->>+ P56: calls
    P56-->>- P1: return
    P1->>+ P57: calls
    P57-->>- P1: return
    P1->>+ P58: calls
    P58-->>- P1: return
    P1->>+ P59: calls
    P59-->>- P1: return
    P1->>+ P60: calls
    P60-->>- P1: return
    P1->>+ P61: calls
    P61-->>- P1: return
    P1->>+ P62: calls
    P62-->>- P1: return
    P1->>+ P63: calls
    P63-->>- P1: return
    P1->>+ P64: calls
    P64-->>- P1: return
    P1->>+ P65: calls
    P65-->>- P1: return
    P1->>+ P66: calls
    P66-->>- P1: return
    P1->>+ P67: calls
    P67-->>- P1: return
    P1->>+ P68: calls
    P68-->>- P1: return
    P1->>+ P69: calls
    P69-->>- P1: return
    P1->>+ P70: calls
    P70-->>- P1: return
    P1->>+ P71: calls
    P71-->>- P1: return
    P1->>+ P72: calls
    P72-->>- P1: return
    P1->>+ P73: calls
    P73-->>- P1: return
    P1->>+ P74: calls
    P74-->>- P1: return
    P1->>+ P75: calls
    P75-->>- P1: return
    P1->>+ P76: calls
    P76-->>- P1: return
    P1->>+ P77: calls
    P77-->>- P1: return
    P1->>+ P78: calls
    P78-->>- P1: return
    P1->>+ P79: calls
    P79-->>- P1: return
    P1->>+ P80: calls
    P80-->>- P1: return
    P1->>+ P81: calls
    P81-->>- P1: return
    P1->>+ P82: calls
    P82-->>- P1: return
    P1->>+ P83: calls
    P83-->>- P1: return
    P1->>+ P84: calls
    P84-->>- P1: return
    P1->>+ P85: calls
    P85-->>- P1: return
    P1->>+ P86: calls
    P86-->>- P1: return
    P1->>+ P87: calls
    P87-->>- P1: return
    P1->>+ P88: calls
    P88-->>- P1: return
    P1->>+ P89: calls
    P89-->>- P1: return
    P1->>+ P90: calls
    P90-->>- P1: return
    P1->>+ P91: calls
    P91-->>- P1: return
    P1->>+ P92: calls
    P92-->>- P1: return
    P1->>+ P93: calls
    P93-->>- P1: return
    P1->>+ P94: calls
    P94-->>- P1: return
    P1->>+ P95: calls
    P95-->>- P1: return
    P1->>+ P96: calls
    P96-->>- P1: return
    P1->>+ P97: calls
    P97-->>- P1: return
    P1->>+ P98: calls
    P98-->>- P1: return
    P1->>+ P99: calls
    P99-->>- P1: return
    P1->>+ P100: calls
    P100-->>- P1: return
    P1->>+ P101: calls
    P101-->>- P1: return
    P1->>+ P102: calls
    P102-->>- P1: return
    P1->>+ P103: calls
    P103-->>- P1: return
    P1->>+ P104: calls
    P104-->>- P1: return
    P1->>+ P105: calls
    P105-->>- P1: return
    P1->>+ P106: calls
    P106-->>- P1: return
    P1->>+ P107: calls
    P107-->>- P1: return
    P1->>+ P108: calls
    P108-->>- P1: return
    P1->>+ P17: calls
    P17-->>- P1: return
    P1->>+ P109: calls
    P109-->>- P1: return
    P1->>+ P110: calls
    P110-->>- P1: return
    P1->>+ P111: calls
    P111-->>- P1: return
    P1->>+ P112: calls
    P112-->>- P1: return
    P1->>+ P113: calls
    P113-->>- P1: return
    P1->>+ P114: calls
    P114-->>- P1: return
    P1->>+ P115: calls
    P115-->>- P1: return
    P1->>+ P116: calls
    P116-->>- P1: return
    P1->>+ P117: calls
    P117-->>- P1: return
    P1->>+ P118: calls
    P118-->>- P1: return
    P1->>+ P119: calls
    P119-->>- P1: return
    P1->>+ P120: calls
    P120-->>- P1: return
    P1->>+ P121: calls
    P121-->>- P1: return
    P1->>+ P122: calls
    P122-->>- P1: return
    P1->>+ P123: calls
    P123-->>- P1: return
    P1->>+ P124: calls
    P124-->>- P1: return
    P1->>+ P125: calls
    P125-->>- P1: return
    P1->>+ P126: calls
    P126-->>- P1: return
    P1->>+ P127: calls
    P127-->>- P1: return
    P1->>+ P128: calls
    P128-->>- P1: return
    P1->>+ P129: calls
    P129-->>- P1: return
    P1->>+ P130: calls
    P130-->>- P1: return
    P1->>+ P131: calls
    P131-->>- P1: return
    P1->>+ P132: calls
    P132-->>- P1: return
    P1->>+ P133: calls
    P133-->>- P1: return
    P1->>+ P134: calls
    P134-->>- P1: return
    P1->>+ P135: calls
    P135-->>- P1: return
    P1->>+ P136: calls
    P136-->>- P1: return
    P1->>+ P137: calls
    P137-->>- P1: return
    P1->>+ P138: calls
    P138-->>- P1: return
    P1->>+ P139: calls
    P139-->>- P1: return
    P1->>+ P140: calls
    P140-->>- P1: return
    P1->>+ P141: calls
    P141-->>- P1: return
    P1->>+ P142: calls
    P142-->>- P1: return
    P1->>+ P143: calls
    P143-->>- P1: return
    P1->>+ P144: calls
    P144-->>- P1: return
    P1->>+ P145: calls
    P145-->>- P1: return
    P1->>+ P146: calls
    P146-->>- P1: return
    P1->>+ P147: calls
    P147-->>- P1: return
    P1->>+ P148: calls
    P148-->>- P1: return
    P1->>+ P149: calls
    P149-->>- P1: return
    P1->>+ P150: calls
    P150-->>- P1: return
    P1->>+ P151: calls
    P151-->>- P1: return
    P1->>+ P152: calls
    P152-->>- P1: return
    P1->>+ P153: calls
    P153-->>- P1: return
    P1->>+ P154: calls
    P154-->>- P1: return
    P1->>+ P155: calls
    P155-->>- P1: return
    P1->>+ P156: calls
    P156-->>- P1: return
    P1->>+ P157: calls
    P157-->>- P1: return
    P1->>+ P158: calls
    P158-->>- P1: return
    P1->>+ P159: calls
    P159-->>- P1: return
    P1->>+ P160: calls
    P160-->>- P1: return
    P1->>+ P161: calls
    P161-->>- P1: return
    P1->>+ P162: calls
    P162-->>- P1: return
    P1->>+ P163: calls
    P163-->>- P1: return
    P1->>+ P164: calls
    P164-->>- P1: return
    P1->>+ P165: calls
    P165-->>- P1: return
    P0->>+ P2: calls
    P2-->>- P0: return
    P0->>+ P166: calls
    P166-->>- P0: return
    P0->>+ P167: calls
    P167-->>- P0: return
    P0->>+ P26: calls
    P26-->>- P0: return
    P0->>+ P27: calls
    P27-->>- P0: return
    P0->>+ P29: calls
    P29-->>- P0: return
    P0->>+ P168: calls
    P168-->>- P0: return
    P0->>+ P31: calls
    P31-->>- P0: return
    P0->>+ P32: calls
    P32-->>- P0: return
    P0->>+ P36: calls
    P36-->>- P0: return
    P0->>+ P169: calls
    P169-->>- P0: return
    P0->>+ P37: calls
    P37-->>- P0: return
    P0->>+ P38: calls
    P38-->>- P0: return
    P0->>+ P39: calls
    P39-->>- P0: return
    P0->>+ P40: calls
    P40-->>- P0: return
    P0->>+ P43: calls
    P43-->>- P0: return
    P0->>+ P170: calls
    P170-->>- P0: return
    P0->>+ P171: calls
    P171-->>- P0: return
    P0->>+ P172: calls
    P172-->>- P0: return
    P0->>+ P51: calls
    P51-->>- P0: return
    P0->>+ P53: calls
    P53-->>- P0: return
    P0->>+ P56: calls
    P56-->>- P0: return
    P0->>+ P52: calls
    P52-->>- P0: return
    P0->>+ P173: calls
    P173-->>- P0: return
    P0->>+ P63: calls
    P63-->>- P0: return
    P0->>+ P72: calls
    P72-->>- P0: return
    P0->>+ P69: calls
    P69-->>- P0: return
    P0->>+ P88: calls
    P88-->>- P0: return
    P0->>+ P174: calls
    P174-->>- P0: return
```

## Connections by Relation

### calls
- [[load()]] `INFERRED`
- [[build_project_detail_context()]] `INFERRED`
- [[catalog_name_key()]] `EXTRACTED`
- [[_render_quote_form()]] `INFERRED`
- [[_hydrate_quote_for_display()]] `INFERRED`
- [[quote_pdf_editor()]] `INFERRED`
- [[mobile_generate_pdf()]] `INFERRED`
- [[_build_quote_workbook()]] `INFERRED`
- [[sync_ldm_bundles()]] `INFERRED`
- [[import_ldm_pdf_create()]] `INFERRED`
- [[export_data()]] `INFERRED`
- [[_build_resumen()]] `INFERRED`
- [[edit_quote()]] `INFERRED`
- [[view_quote()]] `INFERRED`
- [[edit_ldm()]] `INFERRED`
- [[import_ldm_pdf_map()]] `INFERRED`
- [[_bundle_suggestion_ldm()]] `INFERRED`
- [[_quote_preview_from_csv()]] `INFERRED`
- [[_parse_quote_items()]] `INFERRED`
- [[_parse_ldm_items()]] `INFERRED`

### contains
- [[catalog.py]] `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*