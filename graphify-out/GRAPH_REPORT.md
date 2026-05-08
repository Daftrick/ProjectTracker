# Graph Report - ProjectTracker  (2026-05-08)

## Corpus Check
- 54 files · ~83,662 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 855 nodes · 1900 edges · 33 communities detected
- Extraction: 73% EXTRACTED · 27% INFERRED · 0% AMBIGUOUS · INFERRED: 512 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 39|Community 39]]

## God Nodes (most connected - your core abstractions)
1. `load()` - 109 edges
2. `save()` - 75 edges
3. `today()` - 38 edges
4. `build_project_detail_context()` - 23 edges
5. `catalog_maps()` - 21 edges
6. `active_drive_paths()` - 21 edges
7. `compute_consistency()` - 20 edges
8. `parse_quote_csv()` - 18 edges
9. `load_config()` - 17 edges
10. `Quote Project Form Template (Advanced)` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Catalog Hydration Logic` --semantically_similar_to--> `Consistency COT vs LDM Module`  [INFERRED] [semantically similar]
  logica_cuantificaciones.txt → VERSIONES.md
- `Lista de Materiales (LDM) Data Structure` --implements--> `materials.py import_ldm_csv route`  [INFERRED]
  REFERENCIA_ESTRUCTURAS_CSV.txt → tracker/routes/materials.py
- `CSV→LDM Import Diff Algorithm` --rationale_for--> `csv_import.py parse_ldm_csv()`  [INFERRED]
  logica_cuantificaciones.txt → tracker/csv_import.py
- `CSV→LDM Import Diff Algorithm` --rationale_for--> `materials.py import_ldm_csv route`  [INFERRED]
  logica_cuantificaciones.txt → tracker/routes/materials.py
- `CSV→LDM Import Diff Algorithm` --semantically_similar_to--> `Deleted Catalog Audit System`  [INFERRED] [semantically similar]
  logica_cuantificaciones.txt → VERSIONES.md

## Hyperedges (group relationships)
- **he_delete_pattern** — base_modal_del, base_confirm_js, fi_table, tm_cards, cat_impact, pv_table [EXTRACTED 1.00]
- **he_admin_crud** — fi_tpl, tm_tpl, cat_tpl, pv_tpl [INFERRED 0.95]
- **he_session_close** — ver_current, ver_changelog, rm_checklist [EXTRACTED 1.00]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (102): activate_bundle_version_route(), add_bundle_version_route(), add_comparison_ignored(), api_catalogo(), api_catalogo_add(), api_catalogo_impact(), bulk_delete_catalogo(), bundles() (+94 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (72): ldm_pdf(), _project_drive_folder(), _blank_project_form_state(), create_delivery(), create_drive_folder(), new_project(), Crea la carpeta Drive del proyecto si aún no existe., serve_project_file() (+64 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (59): _attach_csv_item_metadata(), _clean_form_text(), _csv_already_imported(), _csv_item_lookup(), _csv_number(), _csv_path_for_project(), edit_ldm(), _find_project() (+51 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (61): LdmSyncTest, MaterialsSyncRouteTest, Pruebas de sincronizacion parcial LDM desde bundles., active_ignored_items(), _clean(), ignored_catalog_ids(), ignored_catalog_map(), normalize_ignored_item() (+53 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (66): Inyeccion app_version via Context Processor, Status Badges CSS bs-* ps-* src-*, Bootstrap Icons 1.11.3 CDN, Bootstrap 5.3.2 CDN, JS confirmDelete y submitFormWithConfirm, Flash Messages Display, Base Layout Template base.html, Modal Confirmacion Destructiva #modalConfirmDelete (+58 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (48): API Endpoint /api/catalogo/add, API Endpoint /api/catalogo/bulk-delete, API Endpoint /api/catalogo, Audit Deleted Catalog Template, Base Layout Template, Bundle Entity (COT Commercial Item + LDM Components), Bundles Template, Catalog Inline AJAX Edit Pattern (+40 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (39): catalog.py hydrate_quote/ldm(), CLAUDE.md Graphify Rules, consistency.py compute_consistency(), csv_import.py parse_ldm_csv(), CSV Import API Routes (Pending), Catálogo Data Structure, Cotización al Cliente (COT) Data Structure, Lista de Materiales (LDM) Data Structure (+31 more)

### Community 7 - "Community 7"
Cohesion: 0.13
Nodes (23): ProjectViewTest, _as_float(), build_consistency_view(), build_drive_scan_view(), build_ldm_row_views(), build_quote_row_views(), build_task_row_views(), _bundle_component_view() (+15 more)

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (13): AggregateLdmItemsTest, AggregateQuoteItemsTest, BundleConsistencyIntegrationTest, ClassifyMarginTest, CompareItemsTest, ComputeConsistencyTest, IgnoredItemsConsistencyTest, _l_item() (+5 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (15): IdFactory, ProjectServicesTest, check_blocked(), currency(), fdate(), get_progress(), today_short(), apply_task_status_change() (+7 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (7): ApiCatalogoTest, FilterCatalogTest, ListCategoriesTest, MatchItemTest, Pruebas para tracker.catalog_search y la API /api/catalogo., Smoke-test del endpoint JSON; no muta datos., TokenizeTest

### Community 11 - "Community 11"
Cohesion: 0.17
Nodes (24): activate_bundle_version(), add_bundle_version(), bundle_by_catalog_item_id(), _clean(), create_bundle(), delete_bundle_version(), expand_quote_bundles(), get_active_bundle_version() (+16 more)

### Community 12 - "Community 12"
Cohesion: 0.21
Nodes (12): ValidatorsTest, _clean(), _deleted_catalog_item_at(), _is_blank(), _parse_float(), _parse_ldm_items(), _parse_quote_items(), _validate_iso_date() (+4 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (14): AdminFilterHelpersTest, AdminFilterRouteTest, Pruebas de filtros administrativos para proveedores y fichas., filter_fichas(), filter_proveedores(), _indexed(), list_field_values(), _matches_tokens() (+6 more)

### Community 14 - "Community 14"
Cohesion: 0.19
Nodes (16): QuoteCsvImportTest, catalog_name_key(), sanitize_pdf_text(), _build_catalog_index(), _clean(), _column_index(), _detect_dialect(), _find_header_row() (+8 more)

### Community 15 - "Community 15"
Cohesion: 0.18
Nodes (13): LdmCsvImportTest, _build_catalog_index(), _clean(), _detect_dialect(), _first_value(), _header_key(), _match_catalog(), _parse_float() (+5 more)

### Community 16 - "Community 16"
Cohesion: 0.24
Nodes (18): catalog_description_lookup(), build_ldm_pdf(), build_quote_pdf(), format_date_long(), money_pdf(), note_lines(), quote_catalog_description(), quote_cover_copy() (+10 more)

### Community 17 - "Community 17"
Cohesion: 0.17
Nodes (15): api_catalogo_categorias(), Lista única de categorías existentes (para datalists/filtros)., Lista única de categorías existentes (para datalists/filtros)., Lista única de categorías existentes (para datalists/filtros)., _indexable_text(), list_categories(), match_item(), _normalize() (+7 more)

### Community 18 - "Community 18"
Cohesion: 0.36
Nodes (1): AdminFormsTest

### Community 19 - "Community 19"
Cohesion: 0.22
Nodes (2): AdminBundlesRoutesTest, Smoke tests de UI Admin para bundles y reglas COT/LDM.

### Community 20 - "Community 20"
Cohesion: 0.25
Nodes (2): BundleVersioningTest, ExpandQuoteBundlesTest

### Community 21 - "Community 21"
Cohesion: 0.33
Nodes (1): ConversionRulesTest

### Community 22 - "Community 22"
Cohesion: 0.33
Nodes (2): ProjectDetailBundleUITest, Smoke tests for the bundle technical consistency UI in project_detail.html.

### Community 23 - "Community 23"
Cohesion: 0.33
Nodes (2): MaterialsCsvExportTest, Tests for exporting an existing LDM as CSV.

### Community 24 - "Community 24"
Cohesion: 0.4
Nodes (5): audit_deleted_catalog(), Audit all quotes and LDMs for deleted catalog items, Audit all quotes and LDMs for deleted catalog items, audit_deleted_catalog_items(), Audit records for deleted catalog items and return summary statistics.      Args

### Community 25 - "Community 25"
Cohesion: 0.4
Nodes (1): ComparisonIgnoredTest

### Community 26 - "Community 26"
Cohesion: 0.4
Nodes (2): AuditDeletedCatalogRouteTest, Tests for the deleted catalog audit route.

### Community 27 - "Community 27"
Cohesion: 0.4
Nodes (1): QuoteCsvImportRouteTest

### Community 28 - "Community 28"
Cohesion: 0.67
Nodes (2): _is_truthy(), Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.

### Community 29 - "Community 29"
Cohesion: 0.67
Nodes (1): fpdf2 Dependency

### Community 30 - "Community 30"
Cohesion: 0.67
Nodes (3): Flask Dependency, openpyxl Dependency, Tech Stack Declaration

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (2): Data Integrity Rules (R1-R7), ProjectTracker System Rationale

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): Roadmap Completed Features

## Knowledge Gaps
- **152 isolated node(s):** `Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.`, `Asegura que cada artículo tenga el campo `categoria` (default '').      Migració`, `LRU cache for drive folder scans with TTL and mtime-based invalidation`, `Get folder modification time for invalidation`, `Create cache key from folder path and parameters` (+147 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 18`** (9 nodes): `AdminFormsTest`, `.assert_invalid_form_preserved()`, `.setUp()`, `.test_catalogo_invalid_form_preserves_capture()`, `.test_fichas_invalid_form_preserves_capture()`, `.test_proveedores_invalid_form_preserves_capture()`, `.test_settings_invalid_path_preserves_capture()`, `.test_team_invalid_form_preserves_capture()`, `test_admin_forms.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (9 nodes): `AdminBundlesRoutesTest`, `._fake_load()`, `.test_bundles_page_loads()`, `.test_comparison_rules_page_loads()`, `.test_create_bundle_persists_bundle()`, `.test_create_comparison_rule_persists_rule()`, `test_admin_bundles_routes.py`, `Smoke tests de UI Admin para bundles y reglas COT/LDM.`, `setUpClass()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (8 nodes): `BundleVersioningTest`, `.test_add_activate_and_delete_version()`, `.test_cannot_delete_only_version()`, `.test_create_bundle_has_active_v1()`, `ExpandQuoteBundlesTest`, `.test_expands_quote_bundle_components()`, `.test_unmapped_quote_items_are_preserved()`, `test_bundles.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (6 nodes): `ConversionRulesTest`, `.test_aggregate_ldm_converts_to_expected_id()`, `.test_compare_expected_vs_actual_marks_shortage_and_excess()`, `.test_ldm_piece_to_cot_linear_meter()`, `.test_tolerance_accepts_small_differences()`, `test_comparison_rules.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (6 nodes): `ProjectDetailBundleUITest`, `.test_materials_tab_exposes_csv_export_for_existing_ldms()`, `.test_materials_tab_exposes_partial_bundle_sync()`, `.test_template_contains_bundle_technical_consistency_section()`, `test_project_detail_bundle_ui.py`, `Smoke tests for the bundle technical consistency UI in project_detail.html.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (6 nodes): `MaterialsCsvExportTest`, `._fake_load()`, `.test_exports_existing_ldm_without_creating_a_new_list()`, `test_materials_csv_export.py`, `Tests for exporting an existing LDM as CSV.`, `setUpClass()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (5 nodes): `ComparisonIgnoredTest`, `.test_filters_by_scope_and_active()`, `.test_split_ignored_linked()`, `.test_summarize_ignored()`, `test_comparison_ignored.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (5 nodes): `AuditDeletedCatalogRouteTest`, `.test_audit_deleted_catalog_loads_materiales_for_ldms()`, `test_audit_deleted_catalog_route.py`, `Tests for the deleted catalog audit route.`, `setUpClass()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (5 nodes): `test_quote_csv_import_route.py`, `QuoteCsvImportRouteTest`, `._fake_load()`, `.test_import_quote_csv_renders_editable_preview()`, `setUpClass()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (3 nodes): `app.py`, `_is_truthy()`, `Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (3 nodes): `pdfs.py build_ldm_pdf()`, `pdfs.py build_quote_pdf()`, `fpdf2 Dependency`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (2 nodes): `Data Integrity Rules (R1-R7)`, `ProjectTracker System Rationale`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `Roadmap Completed Features`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load()` connect `Community 0` to `Community 1`, `Community 2`, `Community 9`, `Community 16`, `Community 17`, `Community 24`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `build_project_detail_context()` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 7`, `Community 9`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `save()` connect `Community 0` to `Community 1`, `Community 2`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 108 inferred relationships involving `load()` (e.g. with `get_progress()` and `migrate_catalog_fields()`) actually correct?**
  _`load()` has 108 INFERRED edges - model-reasoned connections that need verification._
- **Are the 74 inferred relationships involving `save()` (e.g. with `migrate_catalog_fields()` and `migrate_task_statuses()`) actually correct?**
  _`save()` has 74 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `today()` (e.g. with `next_quote_number()` and `build_scope_task()`) actually correct?**
  _`today()` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `build_project_detail_context()` (e.g. with `load()` and `check_blocked()`) actually correct?**
  _`build_project_detail_context()` has 16 INFERRED edges - model-reasoned connections that need verification._