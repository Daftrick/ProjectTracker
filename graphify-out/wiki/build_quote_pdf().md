# build_quote_pdf()

> God node · 38 connections · [/Users/macbook/ProjectTracker/tracker/pdfs.py](file:///Users/macbook/ProjectTracker/tracker/pdfs.py#L241)

## Call Trace Diagram

```mermaid
sequenceDiagram
    participant P0 as build_quote_pdf()
    participant P1 as main()
    participant P2 as load()
    participant P3 as catalog_maps()
    participant P4 as build_project_detail_context()
    participant P5 as import_ldm_csv_upload()
    participant P6 as quote_pdf_editor()
    participant P7 as .snapshot()
    participant P8 as ._get_project()
    participant P9 as _hydrate_quote_for_display()
    participant P10 as _find_project()
    participant P11 as new_quote()
    participant P12 as mobile_generate_pdf()
    participant P13 as sync_ldm_bundles()
    participant P14 as import_ldm_pdf_create()
    participant P15 as add_bundle_version_route()
    participant P16 as .close()
    participant P17 as new_ldm()
    participant P18 as bundles()
    participant P19 as export_data()
    participant P20 as edit_quote()
    participant P21 as view_quote()
    participant P22 as edit_ldm()
    participant P23 as import_ldm_pdf_map()
    participant P24 as catalogo()
    participant P25 as update_bundle_version()
    participant P26 as import_quote_csv()
    participant P27 as _bundle_suggestion_ldm()
    participant P28 as mobile_add_item()
    participant P29 as transaction()
    participant P30 as check_document_access()
    participant P31 as _load_company()
    participant P32 as ldm_pdf_editor()
    participant P33 as _load_pdf_import()
    participant P34 as update_bundle()
    participant P35 as proveedores()
    participant P36 as fichas()
    participant P37 as team()
    participant P38 as _fill_bundle_snapshots()
    participant P39 as purge_quote_deleted_catalog_items()
    participant P40 as purge_deleted_item()
    participant P41 as dashboard()
    participant P42 as kanban()
    participant P43 as new_project()
    participant P44 as _hydrate_quote_for_display()
    participant P45 as mobile_items()
    participant P46 as ._status()
    participant P47 as .test_unpaid_deletion_preserves_other_projects_payments()
    participant P48 as _migrate_quote_approval()
    participant P49 as _render_ldm_form()
    participant P50 as _bundle_sync_suggestions()
    participant P51 as ldm_pdf()
    participant P52 as _render_catalogo()
    participant P53 as _render_proveedores()
    participant P54 as edit_catalogo()
    participant P55 as api_catalogo_add()
    participant P56 as activate_bundle_version_route()
    participant P57 as delete_bundle_version_route()
    participant P58 as empresa_logo()
    participant P59 as set_quote_status_route()
    participant P60 as quote_pdf()
    participant P61 as update_stage_budget()
    participant P62 as _find_project()
    participant P63 as .test_only_admin_can_delete_project_even_with_all_permissions()
    participant P64 as .test_transaction_exception_discards_all_changes()
    participant P65 as migrate_catalog_fields()
    participant P66 as migrate_catalog_disciplina()
    participant P67 as catalog_description_lookup()
    participant P68 as get_alcances()
    participant P69 as api_ldm_set_costo()
    participant P70 as purge_ldm_deleted_catalog_items()
    participant P71 as _render_fichas()
    participant P72 as _render_bundles()
    participant P73 as add_payment_route()
    participant P74 as approve_quote_route()
    participant P75 as quote_excel()
    participant P76 as restore_deleted_item()
    participant P77 as preserve_deleted_item()
    participant P78 as quote_resumen_excel()
    participant P79 as quote_csv_export()
    participant P80 as quote_duplicate()
    participant P81 as quote_templates()
    participant P82 as add_doc_checklist()
    participant P83 as mobile_review()
    participant P84 as quote_templates()
    participant P85 as .setUp()
    participant P86 as .setUp()
    participant P87 as .test_closed_project_can_be_read_and_paid_then_reopened_to_edit()
    participant P88 as .test_catalog_invalid_buy_size_is_rejected_without_mutation()
    participant P89 as .test_each_permission_is_enforced_individually()
    participant P90 as .test_every_scoped_quote_and_ldm_route_checks_ownership()
    participant P91 as .test_failed_request_discards_pending_writes_and_releases_lock()
    participant P92 as .setUp()
    participant P93 as .setUp()
    participant P94 as .test_update_stage_budget_skips_without_template()
    participant P95 as .setUp()
    participant P96 as .setUp()
    participant P97 as .setUp()
    participant P98 as .setUp()
    participant P99 as .setUp()
    participant P100 as .test_override_survives_later_project_client_change()
    participant P101 as .setUp()
    participant P102 as .test_api_catalogo_add_accepts_multiline_nombre_and_descripcion()
    participant P103 as .setUp()
    participant P104 as .setUp()
    participant P105 as .setUp()
    participant P106 as get_progress()
    participant P107 as _csv_already_imported()
    participant P108 as ldm_csv()
    participant P109 as delete_ldm()
    participant P110 as set_ldm_cot()
    participant P111 as _render_team()
    participant P112 as delete_catalogo()
    participant P113 as migrate_catalog_marca()
    participant P114 as bulk_delete_catalogo()
    participant P115 as api_catalogo_categorias()
    participant P116 as _catalog_by_id()
    participant P117 as edit_proveedor()
    participant P118 as _find_project()
    participant P119 as quote_resumen_pdf()
    participant P120 as all_quotes()
    participant P121 as all_payments()
    participant P122 as audit_deleted_catalog()
    participant P123 as _find_project()
    participant P124 as toggle_obra()
    participant P125 as update_project()
    participant P126 as update_project_status()
    participant P127 as close_project()
    participant P128 as delete_project()
    participant P129 as update_stage_status()
    participant P130 as toggle_doc_checklist()
    participant P131 as delete_doc_checklist()
    participant P132 as mobile_remove_item()
    participant P133 as .test_closed_project_shows_readonly_badge_not_select()
    participant P134 as .test_payments_button_visible_even_for_closed_project()
    participant P135 as .test_catalog_decimal_comma_works_for_create_and_edit()
    participant P136 as .test_payment_rejects_nonfinite_amounts_and_invalid_dates()
    participant P137 as .test_transaction_preserves_two_concurrent_request_updates()
    participant P138 as .test_transaction_serializes_separate_server_processes()
    participant P139 as ._get_project()
    participant P140 as .test_upload_stores_pdf_import_payload_outside_cookie_session()
    participant P141 as .setUp()
    participant P142 as .test_creates_quote_with_j_sequence_and_qty_one()
    participant P143 as .test_view_page_hides_unidad_and_cantidad_columns()
    participant P144 as .test_second_quote_increments_j_sequence()
    participant P145 as .test_new_quote_with_client_unchanged_has_no_override()
    participant P146 as .test_new_quote_with_edited_client_saves_override()
    participant P147 as .test_edit_quote_updates_proposal_for()
    participant P148 as .test_description_with_special_chars_is_escaped_as_text_content()
    participant P149 as .setUp()
    participant P150 as .setUp()
    participant P151 as get_disciplinas()
    participant P152 as bulk_edit_catalogo()
    participant P153 as api_catalogo()
    participant P154 as _catalog_sorted_by_name()
    participant P155 as delete_bundle()
    participant P156 as delete_proveedor()
    participant P157 as link_ficha()
    participant P158 as unlink_ficha()
    participant P159 as delete_ficha()
    participant P160 as delete_member()
    participant P161 as delete_quote()
    participant P162 as quote_resumen()
    participant P163 as reopen_project()
    participant P164 as delete_delivery()
    participant P165 as .test_multiline_description_round_trips_through_save()
    participant P166 as api_catalogo_impact()
    participant P167 as mobile_projects()
    participant P168 as save()
    participant P169 as validate_quote_form()
    participant P170 as create_app()
    participant P171 as init_db()
    participant P172 as verify_credentials()
    participant P173 as create_user()
    participant P174 as get_user_by_username()
    participant P175 as set_user_permissions()
    participant P176 as set_user_active()
    participant P177 as _default_admin_config()
    participant P178 as quote_cover_copy()
    participant P179 as _safe_text()
    participant P180 as resolve_quote_proposal_for()
    participant P181 as resolve_quote_terms()
    participant P182 as quote_section_groups()
    participant P183 as quote_project_basis_note()
    participant P184 as ._render_text()
    participant P185 as quote_logo_path()
    participant P186 as _register_pdf_fonts()
    participant P187 as _fitted_cell()
    participant P188 as format_date_long()
    participant P189 as _hex_to_rgb()
    participant P190 as money_pdf()
    participant P191 as quote_catalog_description()
    participant P192 as note_lines()
    participant P193 as .test_pdf_uses_local_terms_and_embeds_lato_in_both_cover_modes()
    participant P194 as .test_large_table_amounts_stay_inside_their_columns()
    participant P195 as quote_type_has_quantities()
    participant P196 as quote_scope_paragraphs()
    participant P197 as .test_pdf_reflects_project_client_over_stale_quote_snapshot()
    participant P198 as .test_pdf_falls_back_to_quote_client_snapshot_when_project_has_none()
    participant P199 as .test_long_description_does_not_orphan_words_after_wrap()
    participant P200 as .test_cover_long_name_remains_complete_at_requested_size_without_overlap()
    participant P201 as .test_cover_name_saved_in_pdf_editor_is_shared_with_quote_and_pdf()
    participant P202 as .test_pdf_with_bundle_item_renders_without_error()
    participant P203 as .test_bundle_breakdown_renders_quantities_without_component_prices()
    participant P204 as .test_specs_terms_and_notes_render_as_independent_sections()
    participant P205 as .test_discount_renders_before_tax_in_both_totals_boxes()
    participant P206 as .test_no_discount_omits_discount_row()
    participant P207 as .test_no_unit_or_qty_columns_rendered()
    P0->>+ P1: calls
    P1-->>- P0: return
    P1->>+ P2: calls
    P2-->>- P1: return
    P2->>+ P3: calls
    P3-->>- P2: return
    P2->>+ P4: calls
    P4-->>- P2: return
    P2->>+ P5: calls
    P5-->>- P2: return
    P2->>+ P6: calls
    P6-->>- P2: return
    P2->>+ P1: calls
    P1-->>- P2: return
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
    P2->>+ P147: calls
    P147-->>- P2: return
    P2->>+ P148: calls
    P148-->>- P2: return
    P2->>+ P149: calls
    P149-->>- P2: return
    P2->>+ P150: calls
    P150-->>- P2: return
    P2->>+ P151: calls
    P151-->>- P2: return
    P2->>+ P152: calls
    P152-->>- P2: return
    P2->>+ P153: calls
    P153-->>- P2: return
    P2->>+ P154: calls
    P154-->>- P2: return
    P2->>+ P155: calls
    P155-->>- P2: return
    P2->>+ P156: calls
    P156-->>- P2: return
    P2->>+ P157: calls
    P157-->>- P2: return
    P2->>+ P158: calls
    P158-->>- P2: return
    P2->>+ P159: calls
    P159-->>- P2: return
    P2->>+ P160: calls
    P160-->>- P2: return
    P2->>+ P161: calls
    P161-->>- P2: return
    P2->>+ P162: calls
    P162-->>- P2: return
    P2->>+ P163: calls
    P163-->>- P2: return
    P2->>+ P164: calls
    P164-->>- P2: return
    P2->>+ P165: calls
    P165-->>- P2: return
    P2->>+ P166: calls
    P166-->>- P2: return
    P2->>+ P167: calls
    P167-->>- P2: return
    P1->>+ P168: calls
    P168-->>- P1: return
    P1->>+ P0: calls
    P0-->>- P1: return
    P1->>+ P169: calls
    P169-->>- P1: return
    P1->>+ P170: calls
    P170-->>- P1: return
    P1->>+ P171: calls
    P171-->>- P1: return
    P1->>+ P172: calls
    P172-->>- P1: return
    P1->>+ P173: calls
    P173-->>- P1: return
    P1->>+ P174: calls
    P174-->>- P1: return
    P1->>+ P175: calls
    P175-->>- P1: return
    P1->>+ P176: calls
    P176-->>- P1: return
    P1->>+ P177: calls
    P177-->>- P1: return
    P0->>+ P178: calls
    P178-->>- P0: return
    P0->>+ P12: calls
    P12-->>- P0: return
    P0->>+ P179: calls
    P179-->>- P0: return
    P0->>+ P180: calls
    P180-->>- P0: return
    P0->>+ P181: calls
    P181-->>- P0: return
    P0->>+ P19: calls
    P19-->>- P0: return
    P0->>+ P182: calls
    P182-->>- P0: return
    P0->>+ P183: calls
    P183-->>- P0: return
    P0->>+ P31: calls
    P31-->>- P0: return
    P0->>+ P184: calls
    P184-->>- P0: return
    P0->>+ P60: calls
    P60-->>- P0: return
    P0->>+ P185: calls
    P185-->>- P0: return
    P0->>+ P186: calls
    P186-->>- P0: return
    P0->>+ P187: calls
    P187-->>- P0: return
    P0->>+ P67: calls
    P67-->>- P0: return
    P0->>+ P188: calls
    P188-->>- P0: return
    P0->>+ P189: calls
    P189-->>- P0: return
    P0->>+ P190: calls
    P190-->>- P0: return
    P0->>+ P191: calls
    P191-->>- P0: return
    P0->>+ P192: calls
    P192-->>- P0: return
    P0->>+ P193: calls
    P193-->>- P0: return
    P0->>+ P194: calls
    P194-->>- P0: return
    P0->>+ P195: calls
    P195-->>- P0: return
    P0->>+ P119: calls
    P119-->>- P0: return
    P0->>+ P196: calls
    P196-->>- P0: return
    P0->>+ P197: calls
    P197-->>- P0: return
    P0->>+ P198: calls
    P198-->>- P0: return
    P0->>+ P199: calls
    P199-->>- P0: return
    P0->>+ P200: calls
    P200-->>- P0: return
    P0->>+ P201: calls
    P201-->>- P0: return
    P0->>+ P202: calls
    P202-->>- P0: return
    P0->>+ P203: calls
    P203-->>- P0: return
    P0->>+ P204: calls
    P204-->>- P0: return
    P0->>+ P205: calls
    P205-->>- P0: return
    P0->>+ P206: calls
    P206-->>- P0: return
    P0->>+ P207: calls
    P207-->>- P0: return
```

## Connections by Relation

### calls
- [[main()]] `INFERRED`
- [[quote_cover_copy()]] `EXTRACTED`
- [[mobile_generate_pdf()]] `INFERRED`
- [[_safe_text()]] `EXTRACTED`
- [[resolve_quote_proposal_for()]] `INFERRED`
- [[resolve_quote_terms()]] `INFERRED`
- [[export_data()]] `INFERRED`
- [[quote_section_groups()]] `INFERRED`
- [[quote_project_basis_note()]] `EXTRACTED`
- [[_load_company()]] `EXTRACTED`
- [[._render_text()]] `INFERRED`
- [[quote_pdf()]] `INFERRED`
- [[quote_logo_path()]] `EXTRACTED`
- [[_register_pdf_fonts()]] `EXTRACTED`
- [[_fitted_cell()]] `EXTRACTED`
- [[catalog_description_lookup()]] `INFERRED`
- [[format_date_long()]] `EXTRACTED`
- [[_hex_to_rgb()]] `EXTRACTED`
- [[money_pdf()]] `EXTRACTED`
- [[quote_catalog_description()]] `EXTRACTED`

### contains
- [[pdfs.py]] `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*