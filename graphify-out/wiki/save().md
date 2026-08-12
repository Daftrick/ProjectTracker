# save()

> God node · 109 connections · [/Users/macbook/ProjectTracker/tracker/storage.py](file:///Users/macbook/ProjectTracker/tracker/storage.py#L49)

## Call Trace Diagram

```mermaid
sequenceDiagram
    participant P0 as save()
    participant P1 as import_ldm_csv_upload()
    participant P2 as load()
    participant P3 as catalog_maps()
    participant P4 as build_project_detail_context()
    participant P5 as ._get_project()
    participant P6 as _hydrate_quote_for_display()
    participant P7 as quote_pdf_editor()
    participant P8 as new_quote()
    participant P9 as mobile_generate_pdf()
    participant P10 as _find_project()
    participant P11 as sync_ldm_bundles()
    participant P12 as import_ldm_pdf_create()
    participant P13 as add_bundle_version_route()
    participant P14 as new_ldm()
    participant P15 as bundles()
    participant P16 as export_data()
    participant P17 as edit_quote()
    participant P18 as view_quote()
    participant P19 as edit_ldm()
    participant P20 as import_ldm_pdf_map()
    participant P21 as update_bundle_version()
    participant P22 as import_quote_csv()
    participant P23 as _bundle_suggestion_ldm()
    participant P24 as catalogo()
    participant P25 as _load_company()
    participant P26 as _load_pdf_import()
    participant P27 as update_bundle()
    participant P28 as proveedores()
    participant P29 as fichas()
    participant P30 as team()
    participant P31 as _fill_bundle_snapshots()
    participant P32 as purge_quote_deleted_catalog_items()
    participant P33 as purge_deleted_item()
    participant P34 as kanban()
    participant P35 as new_project()
    participant P36 as _hydrate_quote_for_display()
    participant P37 as mobile_items()
    participant P38 as main()
    participant P39 as ._status()
    participant P40 as _migrate_quote_approval()
    participant P41 as _render_ldm_form()
    participant P42 as _bundle_sync_suggestions()
    participant P43 as ldm_pdf()
    participant P44 as _render_catalogo()
    participant P45 as _render_proveedores()
    participant P46 as activate_bundle_version_route()
    participant P47 as delete_bundle_version_route()
    participant P48 as empresa_logo()
    participant P49 as quote_pdf()
    participant P50 as update_stage_budget()
    participant P51 as _find_project()
    participant P52 as mobile_add_item()
    participant P53 as migrate_catalog_fields()
    participant P54 as migrate_catalog_disciplina()
    participant P55 as catalog_description_lookup()
    participant P56 as get_alcances()
    participant P57 as purge_ldm_deleted_catalog_items()
    participant P58 as _render_fichas()
    participant P59 as edit_catalogo()
    participant P60 as api_catalogo_add()
    participant P61 as _render_bundles()
    participant P62 as approve_quote_route()
    participant P63 as set_quote_status_route()
    participant P64 as quote_excel()
    participant P65 as restore_deleted_item()
    participant P66 as preserve_deleted_item()
    participant P67 as quote_resumen_excel()
    participant P68 as quote_csv_export()
    participant P69 as quote_duplicate()
    participant P70 as quote_templates()
    participant P71 as add_doc_checklist()
    participant P72 as mobile_review()
    participant P73 as quote_templates()
    participant P74 as .setUp()
    participant P75 as .setUp()
    participant P76 as .setUp()
    participant P77 as .setUp()
    participant P78 as .test_update_stage_budget_skips_without_template()
    participant P79 as .setUp()
    participant P80 as .setUp()
    participant P81 as .setUp()
    participant P82 as .setUp()
    participant P83 as .test_override_survives_later_project_client_change()
    participant P84 as .setUp()
    participant P85 as .test_api_catalogo_add_accepts_multiline_nombre_and_descripcion()
    participant P86 as .setUp()
    participant P87 as .setUp()
    participant P88 as .setUp()
    participant P89 as get_progress()
    participant P90 as _csv_already_imported()
    participant P91 as ldm_csv()
    participant P92 as delete_ldm()
    participant P93 as set_ldm_cot()
    participant P94 as _render_team()
    participant P95 as delete_catalogo()
    participant P96 as migrate_catalog_marca()
    participant P97 as bulk_delete_catalogo()
    participant P98 as api_catalogo_categorias()
    participant P99 as _catalog_by_id()
    participant P100 as edit_proveedor()
    participant P101 as _find_project()
    participant P102 as add_payment_route()
    participant P103 as quote_resumen_pdf()
    participant P104 as all_quotes()
    participant P105 as all_payments()
    participant P106 as audit_deleted_catalog()
    participant P107 as _find_project()
    participant P108 as toggle_obra()
    participant P109 as update_project()
    participant P110 as update_project_status()
    participant P111 as close_project()
    participant P112 as delete_project()
    participant P113 as update_stage_status()
    participant P114 as toggle_doc_checklist()
    participant P115 as delete_doc_checklist()
    participant P116 as mobile_remove_item()
    participant P117 as .test_closed_project_shows_readonly_badge_not_select()
    participant P118 as .test_payments_button_visible_even_for_closed_project()
    participant P119 as ._get_project()
    participant P120 as .test_upload_stores_pdf_import_payload_outside_cookie_session()
    participant P121 as .setUp()
    participant P122 as .test_new_quote_with_client_unchanged_has_no_override()
    participant P123 as .test_new_quote_with_edited_client_saves_override()
    participant P124 as .test_edit_quote_updates_proposal_for()
    participant P125 as .test_description_with_special_chars_is_escaped_as_text_content()
    participant P126 as .setUp()
    participant P127 as .setUp()
    participant P128 as get_disciplinas()
    participant P129 as api_ldm_set_costo()
    participant P130 as bulk_edit_catalogo()
    participant P131 as api_catalogo()
    participant P132 as _catalog_sorted_by_name()
    participant P133 as delete_bundle()
    participant P134 as delete_proveedor()
    participant P135 as link_ficha()
    participant P136 as unlink_ficha()
    participant P137 as delete_ficha()
    participant P138 as delete_member()
    participant P139 as delete_quote()
    participant P140 as quote_resumen()
    participant P141 as dashboard()
    participant P142 as reopen_project()
    participant P143 as delete_delivery()
    participant P144 as .test_multiline_description_round_trips_through_save()
    participant P145 as api_catalogo_impact()
    participant P146 as mobile_projects()
    participant P147 as today()
    participant P148 as parse_ldm_csv()
    participant P149 as new_id()
    participant P150 as validate_csv_catalog_items()
    participant P151 as validate_ldm_form()
    participant P152 as ldm_from_form()
    participant P153 as parse_csv_plano_filename()
    participant P154 as _hydrate_import_items()
    participant P155 as _flash_csv_catalog_errors()
    participant P156 as import_ldm_pdf_upload()
    participant P157 as _build_export_like_xlsx()
    participant P158 as .tearDown()
    participant P159 as .tearDown()
    participant P160 as .tearDown()
    participant P161 as .tearDown()
    participant P162 as .tearDown()
    participant P163 as .tearDown()
    participant P164 as .tearDown()
    participant P165 as .tearDown()
    participant P166 as .tearDown()
    participant P167 as .tearDown()
    participant P168 as .tearDown()
    participant P169 as .tearDown()
    participant P170 as .tearDown()
    participant P171 as .tearDown()
    participant P172 as .tearDown()
    participant P173 as import_json()
    participant P174 as alcances_api_save()
    participant P175 as disciplinas_api_save()
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
    P2->>+ P112: calls
    P112-->>- P2: return
    P2->>+ P113: calls
    P113-->>- P2: return
    P2->>+ P114: calls
    P114-->>- P2: return
    P2->>+ P115: calls
    P115-->>- P2: return
    P2->>+ P116: calls
    P116-->>- P2: return
    P2->>+ P117: calls
    P117-->>- P2: return
    P2->>+ P118: calls
    P118-->>- P2: return
    P2->>+ P119: calls
    P119-->>- P2: return
    P2->>+ P120: calls
    P120-->>- P2: return
    P2->>+ P121: calls
    P121-->>- P2: return
    P2->>+ P122: calls
    P122-->>- P2: return
    P2->>+ P123: calls
    P123-->>- P2: return
    P2->>+ P124: calls
    P124-->>- P2: return
    P2->>+ P125: calls
    P125-->>- P2: return
    P2->>+ P126: calls
    P126-->>- P2: return
    P2->>+ P127: calls
    P127-->>- P2: return
    P2->>+ P128: calls
    P128-->>- P2: return
    P2->>+ P129: calls
    P129-->>- P2: return
    P2->>+ P130: calls
    P130-->>- P2: return
    P2->>+ P131: calls
    P131-->>- P2: return
    P2->>+ P132: calls
    P132-->>- P2: return
    P2->>+ P133: calls
    P133-->>- P2: return
    P2->>+ P134: calls
    P134-->>- P2: return
    P2->>+ P135: calls
    P135-->>- P2: return
    P2->>+ P136: calls
    P136-->>- P2: return
    P2->>+ P137: calls
    P137-->>- P2: return
    P2->>+ P138: calls
    P138-->>- P2: return
    P2->>+ P139: calls
    P139-->>- P2: return
    P2->>+ P140: calls
    P140-->>- P2: return
    P2->>+ P141: calls
    P141-->>- P2: return
    P2->>+ P142: calls
    P142-->>- P2: return
    P2->>+ P143: calls
    P143-->>- P2: return
    P2->>+ P144: calls
    P144-->>- P2: return
    P2->>+ P145: calls
    P145-->>- P2: return
    P2->>+ P146: calls
    P146-->>- P2: return
    P1->>+ P0: calls
    P0-->>- P1: return
    P1->>+ P147: calls
    P147-->>- P1: return
    P1->>+ P148: calls
    P148-->>- P1: return
    P1->>+ P149: calls
    P149-->>- P1: return
    P1->>+ P150: calls
    P150-->>- P1: return
    P1->>+ P10: calls
    P10-->>- P1: return
    P1->>+ P151: calls
    P151-->>- P1: return
    P1->>+ P41: calls
    P41-->>- P1: return
    P1->>+ P152: calls
    P152-->>- P1: return
    P1->>+ P153: calls
    P153-->>- P1: return
    P1->>+ P90: calls
    P90-->>- P1: return
    P1->>+ P154: calls
    P154-->>- P1: return
    P1->>+ P155: calls
    P155-->>- P1: return
    P0->>+ P7: calls
    P7-->>- P0: return
    P0->>+ P8: calls
    P8-->>- P0: return
    P0->>+ P9: calls
    P9-->>- P0: return
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
    P0->>+ P16: calls
    P16-->>- P0: return
    P0->>+ P17: calls
    P17-->>- P0: return
    P0->>+ P19: calls
    P19-->>- P0: return
    P0->>+ P21: calls
    P21-->>- P0: return
    P0->>+ P22: calls
    P22-->>- P0: return
    P0->>+ P24: calls
    P24-->>- P0: return
    P0->>+ P156: calls
    P156-->>- P0: return
    P0->>+ P27: calls
    P27-->>- P0: return
    P0->>+ P28: calls
    P28-->>- P0: return
    P0->>+ P29: calls
    P29-->>- P0: return
    P0->>+ P30: calls
    P30-->>- P0: return
    P0->>+ P32: calls
    P32-->>- P0: return
    P0->>+ P33: calls
    P33-->>- P0: return
    P0->>+ P35: calls
    P35-->>- P0: return
    P0->>+ P37: calls
    P37-->>- P0: return
    P0->>+ P40: calls
    P40-->>- P0: return
    P0->>+ P46: calls
    P46-->>- P0: return
    P0->>+ P47: calls
    P47-->>- P0: return
    P0->>+ P50: calls
    P50-->>- P0: return
    P0->>+ P52: calls
    P52-->>- P0: return
    P0->>+ P157: calls
    P157-->>- P0: return
    P0->>+ P53: calls
    P53-->>- P0: return
    P0->>+ P54: calls
    P54-->>- P0: return
    P0->>+ P57: calls
    P57-->>- P0: return
    P0->>+ P59: calls
    P59-->>- P0: return
    P0->>+ P60: calls
    P60-->>- P0: return
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
    P0->>+ P67: calls
    P67-->>- P0: return
    P0->>+ P69: calls
    P69-->>- P0: return
    P0->>+ P71: calls
    P71-->>- P0: return
    P0->>+ P74: calls
    P74-->>- P0: return
    P0->>+ P75: calls
    P75-->>- P0: return
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
    P0->>+ P92: calls
    P92-->>- P0: return
    P0->>+ P93: calls
    P93-->>- P0: return
    P0->>+ P95: calls
    P95-->>- P0: return
    P0->>+ P96: calls
    P96-->>- P0: return
    P0->>+ P97: calls
    P97-->>- P0: return
    P0->>+ P100: calls
    P100-->>- P0: return
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
    P0->>+ P121: calls
    P121-->>- P0: return
    P0->>+ P125: calls
    P125-->>- P0: return
    P0->>+ P126: calls
    P126-->>- P0: return
    P0->>+ P127: calls
    P127-->>- P0: return
    P0->>+ P129: calls
    P129-->>- P0: return
    P0->>+ P130: calls
    P130-->>- P0: return
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
    P0->>+ P142: calls
    P142-->>- P0: return
    P0->>+ P143: calls
    P143-->>- P0: return
    P0->>+ P158: calls
    P158-->>- P0: return
    P0->>+ P159: calls
    P159-->>- P0: return
    P0->>+ P160: calls
    P160-->>- P0: return
    P0->>+ P161: calls
    P161-->>- P0: return
    P0->>+ P162: calls
    P162-->>- P0: return
    P0->>+ P163: calls
    P163-->>- P0: return
    P0->>+ P164: calls
    P164-->>- P0: return
    P0->>+ P165: calls
    P165-->>- P0: return
    P0->>+ P166: calls
    P166-->>- P0: return
    P0->>+ P167: calls
    P167-->>- P0: return
    P0->>+ P168: calls
    P168-->>- P0: return
    P0->>+ P169: calls
    P169-->>- P0: return
    P0->>+ P170: calls
    P170-->>- P0: return
    P0->>+ P171: calls
    P171-->>- P0: return
    P0->>+ P172: calls
    P172-->>- P0: return
    P0->>+ P173: calls
    P173-->>- P0: return
    P0->>+ P174: calls
    P174-->>- P0: return
    P0->>+ P175: calls
    P175-->>- P0: return
```

## Connections by Relation

### calls
- [[import_ldm_csv_upload()]] `INFERRED`
- [[quote_pdf_editor()]] `INFERRED`
- [[new_quote()]] `INFERRED`
- [[mobile_generate_pdf()]] `INFERRED`
- [[sync_ldm_bundles()]] `INFERRED`
- [[import_ldm_pdf_create()]] `INFERRED`
- [[add_bundle_version_route()]] `INFERRED`
- [[new_ldm()]] `INFERRED`
- [[bundles()]] `INFERRED`
- [[export_data()]] `INFERRED`
- [[edit_quote()]] `INFERRED`
- [[edit_ldm()]] `INFERRED`
- [[update_bundle_version()]] `INFERRED`
- [[import_quote_csv()]] `INFERRED`
- [[catalogo()]] `INFERRED`
- [[import_ldm_pdf_upload()]] `INFERRED`
- [[update_bundle()]] `INFERRED`
- [[proveedores()]] `INFERRED`
- [[fichas()]] `INFERRED`
- [[team()]] `INFERRED`

### contains
- [[storage.py]] `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*