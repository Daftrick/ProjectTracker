# compute_consistency()

> God node · 24 connections · [/Users/macbook/ProjectTracker/tracker/consistency.py](file:///Users/macbook/ProjectTracker/tracker/consistency.py#L408)

## Call Trace Diagram

```mermaid
sequenceDiagram
    participant P0 as compute_consistency()
    participant P1 as build_project_detail_context()
    participant P2 as load()
    participant P3 as catalog_maps()
    participant P4 as import_ldm_csv_upload()
    participant P5 as ._get_project()
    participant P6 as _hydrate_quote_for_display()
    participant P7 as _find_project()
    participant P8 as sync_ldm_bundles()
    participant P9 as import_ldm_pdf_create()
    participant P10 as add_bundle_version_route()
    participant P11 as quote_pdf_editor()
    participant P12 as new_ldm()
    participant P13 as bundles()
    participant P14 as export_data()
    participant P15 as new_quote()
    participant P16 as mobile_generate_pdf()
    participant P17 as edit_ldm()
    participant P18 as import_ldm_pdf_map()
    participant P19 as catalogo()
    participant P20 as update_bundle_version()
    participant P21 as import_quote_csv()
    participant P22 as _bundle_suggestion_ldm()
    participant P23 as proveedores()
    participant P24 as fichas()
    participant P25 as team()
    participant P26 as edit_quote()
    participant P27 as _load_company()
    participant P28 as _load_pdf_import()
    participant P29 as update_bundle()
    participant P30 as purge_quote_deleted_catalog_items()
    participant P31 as purge_deleted_item()
    participant P32 as new_project()
    participant P33 as _hydrate_quote_for_display()
    participant P34 as mobile_items()
    participant P35 as main()
    participant P36 as _migrate_quote_approval()
    participant P37 as _render_ldm_form()
    participant P38 as _bundle_sync_suggestions()
    participant P39 as ldm_pdf()
    participant P40 as _render_catalogo()
    participant P41 as _render_proveedores()
    participant P42 as activate_bundle_version_route()
    participant P43 as delete_bundle_version_route()
    participant P44 as empresa_logo()
    participant P45 as quote_pdf()
    participant P46 as update_stage_budget()
    participant P47 as _find_project()
    participant P48 as mobile_add_item()
    participant P49 as migrate_catalog_fields()
    participant P50 as migrate_catalog_disciplina()
    participant P51 as catalog_description_lookup()
    participant P52 as get_alcances()
    participant P53 as purge_ldm_deleted_catalog_items()
    participant P54 as _render_fichas()
    participant P55 as edit_catalogo()
    participant P56 as api_catalogo_add()
    participant P57 as _render_bundles()
    participant P58 as quote_templates()
    participant P59 as view_quote()
    participant P60 as approve_quote_route()
    participant P61 as quote_excel()
    participant P62 as restore_deleted_item()
    participant P63 as preserve_deleted_item()
    participant P64 as quote_resumen_excel()
    participant P65 as quote_csv_export()
    participant P66 as quote_duplicate()
    participant P67 as add_doc_checklist()
    participant P68 as mobile_review()
    participant P69 as .setUp()
    participant P70 as .test_update_stage_budget_skips_without_template()
    participant P71 as _csv_already_imported()
    participant P72 as ldm_csv()
    participant P73 as delete_ldm()
    participant P74 as set_ldm_cot()
    participant P75 as _render_team()
    participant P76 as delete_catalogo()
    participant P77 as migrate_catalog_marca()
    participant P78 as bulk_delete_catalogo()
    participant P79 as api_catalogo_categorias()
    participant P80 as _catalog_by_id()
    participant P81 as edit_proveedor()
    participant P82 as _find_project()
    participant P83 as quote_resumen_pdf()
    participant P84 as audit_deleted_catalog()
    participant P85 as _find_project()
    participant P86 as update_project()
    participant P87 as update_project_status()
    participant P88 as close_project()
    participant P89 as delete_project()
    participant P90 as update_stage_status()
    participant P91 as toggle_doc_checklist()
    participant P92 as delete_doc_checklist()
    participant P93 as mobile_remove_item()
    participant P94 as .test_upload_stores_pdf_import_payload_outside_cookie_session()
    participant P95 as get_disciplinas()
    participant P96 as get_progress()
    participant P97 as api_ldm_set_costo()
    participant P98 as bulk_edit_catalogo()
    participant P99 as api_catalogo()
    participant P100 as _catalog_sorted_by_name()
    participant P101 as delete_bundle()
    participant P102 as delete_proveedor()
    participant P103 as link_ficha()
    participant P104 as unlink_ficha()
    participant P105 as delete_ficha()
    participant P106 as delete_member()
    participant P107 as delete_quote()
    participant P108 as quote_resumen()
    participant P109 as all_quotes()
    participant P110 as dashboard()
    participant P111 as reopen_project()
    participant P112 as delete_delivery()
    participant P113 as api_catalogo_impact()
    participant P114 as mobile_projects()
    participant P115 as today()
    participant P116 as hydrate_quote()
    participant P117 as pick_active_quote()
    participant P118 as hydrate_ldm()
    participant P119 as is_base_quote_type()
    participant P120 as build_consistency_view()
    participant P121 as build_quote_row_views()
    participant P122 as build_task_row_views()
    participant P123 as build_ldm_row_views()
    participant P124 as check_blocked()
    participant P125 as project_detail()
    participant P126 as .test_build_project_detail_context_groups_and_calculates_totals()
    participant P127 as quote_type_key()
    participant P128 as aggregate_quote_items()
    participant P129 as _round()
    participant P130 as aggregate_ldm_items()
    participant P131 as _safe_float()
    participant P132 as .test_full_report_with_general_quote()
    participant P133 as .test_warning_threshold()
    participant P134 as .test_critical_when_ldm_exceeds_cot()
    participant P135 as _quote_visual_row()
    participant P136 as classify_margin()
    participant P137 as _ldm_visual_row()
    participant P138 as .test_no_general_quote_uses_fallback()
    participant P139 as .test_filters_by_project_id()
    participant P140 as .test_visual_warnings_include_missing_data_and_unlinked_rows()
    participant P141 as .test_active_extras_are_included_in_visual_total()
    participant P142 as _active_base_quotes()
    participant P143 as _active_extra_quotes()
    participant P144 as _catalog_coverage_pct()
    participant P145 as _synthetic_quote()
    participant P146 as _visual_warnings()
    participant P147 as .test_no_data_when_empty()
    P0->>+ P1: calls
    P1-->>- P0: return
    P1->>+ P2: calls
    P2-->>- P1: return
    P2->>+ P3: calls
    P3-->>- P2: return
    P2->>+ P1: calls
    P1-->>- P2: return
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
    P2->>+ P112: calls
    P112-->>- P2: return
    P2->>+ P113: calls
    P113-->>- P2: return
    P2->>+ P114: calls
    P114-->>- P2: return
    P1->>+ P115: calls
    P115-->>- P1: return
    P1->>+ P3: calls
    P3-->>- P1: return
    P1->>+ P0: calls
    P0-->>- P1: return
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
    P1->>+ P96: calls
    P96-->>- P1: return
    P1->>+ P126: calls
    P126-->>- P1: return
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
    P0->>+ P137: calls
    P137-->>- P0: return
    P0->>+ P138: calls
    P138-->>- P0: return
    P0->>+ P139: calls
    P139-->>- P0: return
    P0->>+ P140: calls
    P140-->>- P0: return
    P0->>+ P141: calls
    P141-->>- P0: return
    P0->>+ P142: calls
    P142-->>- P0: return
    P0->>+ P143: calls
    P143-->>- P0: return
    P0->>+ P144: calls
    P144-->>- P0: return
    P0->>+ P145: calls
    P145-->>- P0: return
    P0->>+ P146: calls
    P146-->>- P0: return
    P0->>+ P147: calls
    P147-->>- P0: return
```

## Connections by Relation

### calls
- [[build_project_detail_context()]] `INFERRED`
- [[quote_type_key()]] `INFERRED`
- [[aggregate_quote_items()]] `EXTRACTED`
- [[_round()]] `EXTRACTED`
- [[aggregate_ldm_items()]] `EXTRACTED`
- [[_safe_float()]] `EXTRACTED`
- [[.test_full_report_with_general_quote()]] `INFERRED`
- [[.test_warning_threshold()]] `INFERRED`
- [[.test_critical_when_ldm_exceeds_cot()]] `INFERRED`
- [[_quote_visual_row()]] `EXTRACTED`
- [[classify_margin()]] `EXTRACTED`
- [[_ldm_visual_row()]] `EXTRACTED`
- [[.test_no_general_quote_uses_fallback()]] `INFERRED`
- [[.test_filters_by_project_id()]] `INFERRED`
- [[.test_visual_warnings_include_missing_data_and_unlinked_rows()]] `INFERRED`
- [[.test_active_extras_are_included_in_visual_total()]] `INFERRED`
- [[_active_base_quotes()]] `EXTRACTED`
- [[_active_extra_quotes()]] `EXTRACTED`
- [[_catalog_coverage_pct()]] `EXTRACTED`
- [[_synthetic_quote()]] `EXTRACTED`

### contains
- [[consistency.py]] `EXTRACTED`

### rationale_for
- [[Resumen financiero simple para inyectar en plantillas.]] `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*