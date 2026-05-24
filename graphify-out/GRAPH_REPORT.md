# Graph Report - ProjectTracker  (2026-05-23)

## Corpus Check
- 55 files · ~87,729 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 966 nodes · 2432 edges · 39 communities detected
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 523 edges (avg confidence: 0.8)
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
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 46|Community 46]]

## God Nodes (most connected - your core abstractions)
1. `load()` - 110 edges
2. `save()` - 76 edges
3. `admin.py` - 55 edges
4. `today()` - 39 edges
5. `parse_quote_csv()` - 25 edges
6. `build_project_detail_context()` - 24 edges
7. `catalog_maps()` - 22 edges
8. `active_drive_paths()` - 22 edges
9. `compute_consistency()` - 21 edges
10. `parse_ldm_csv()` - 21 edges

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
Cohesion: 0.05
Nodes (66): ldm_pdf(), _project_drive_folder(), create_delivery(), create_drive_folder(), Crea la carpeta Drive del proyecto si aún no existe., serve_project_file(), quote_excel(), quote_pdf() (+58 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (77): activate_bundle_version_route(), add_bundle_version_route(), add_comparison_ignored(), api_catalogo(), api_catalogo_add(), api_catalogo_categorias(), api_catalogo_impact(), bulk_delete_catalogo() (+69 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (65): dashboard(), audit_deleted_catalog(), _build_quote_workbook(), delete_quote(), edit_quote(), _find_project(), import_quote_csv(), new_quote() (+57 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (62): LdmSyncTest, MaterialsSyncRouteTest, Pruebas de sincronizacion parcial LDM desde bundles., setUpClass(), active_ignored_items(), _clean(), ignored_catalog_ids(), ignored_catalog_map() (+54 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (66): Inyeccion app_version via Context Processor, Status Badges CSS bs-* ps-* src-*, Bootstrap Icons 1.11.3 CDN, Bootstrap 5.3.2 CDN, JS confirmDelete y submitFormWithConfirm, Flash Messages Display, Base Layout Template base.html, Modal Confirmacion Destructiva #modalConfirmDelete (+58 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (25): QuoteCsvImportTest, QuoteSymbolFixturesTest, CSV escrito en cp1252 (fallback ANSI del LISP) debe retornar error         legib, CSV escrito en cp1252 (fallback ANSI del LISP) debe retornar error         legib, CotTubeFixturesTest, Tests parametrizados para importación CSV de tubería conduit.  Cubre los 6 tipos, Metadata #proyecto_clave y #quote_type del archivo COT LISP., Múltiples tipos y diámetros en un solo archivo COT. (+17 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (48): API Endpoint /api/catalogo/add, API Endpoint /api/catalogo/bulk-delete, API Endpoint /api/catalogo, Audit Deleted Catalog Template, Base Layout Template, Bundle Entity (COT Commercial Item + LDM Components), Bundles Template, Catalog Inline AJAX Edit Pattern (+40 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (21): LdmCsvImportTest, CSV escrito en cp1252 (fallback ANSI del LISP) debe retornar error         legib, LdmTubeFixturesTest, Múltiples tipos de tubería en un mismo archivo LDM., Metadata #proveedor y #fecha post-header (formato real del LISP)., Escribe un CSV LDM con header estándar y filas dadas.      meta_rows: lista de t, _write_ldm(), _build_catalog_index() (+13 more)

### Community 8 - "Community 8"
Cohesion: 0.1
Nodes (27): _blank_project_form_state(), delete_delivery(), delete_project(), new_project(), project_detail(), reopen_project(), save_task_note(), settings() (+19 more)

### Community 9 - "Community 9"
Cohesion: 0.13
Nodes (29): ProjectViewTest, check_blocked(), currency(), fdate(), get_progress(), today_short(), _as_float(), build_consistency_view() (+21 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (39): catalog.py hydrate_quote/ldm(), CLAUDE.md Graphify Rules, consistency.py compute_consistency(), csv_import.py parse_ldm_csv(), CSV Import API Routes (Pending), Catálogo Data Structure, Cotización al Cliente (COT) Data Structure, Lista de Materiales (LDM) Data Structure (+31 more)

### Community 11 - "Community 11"
Cohesion: 0.14
Nodes (27): api_ldm_set_costo(), _attach_csv_item_metadata(), _clean_form_text(), _csv_already_imported(), _csv_item_lookup(), _csv_number(), _csv_path_for_project(), delete_ldm() (+19 more)

### Community 12 - "Community 12"
Cohesion: 0.16
Nodes (13): AggregateLdmItemsTest, AggregateQuoteItemsTest, BundleConsistencyIntegrationTest, ClassifyMarginTest, CompareItemsTest, ComputeConsistencyTest, IgnoredItemsConsistencyTest, _l_item() (+5 more)

### Community 13 - "Community 13"
Cohesion: 0.08
Nodes (8): ApiCatalogoTest, FilterCatalogTest, ListCategoriesTest, MatchItemTest, Pruebas para tracker.catalog_search y la API /api/catalogo., Smoke-test del endpoint JSON; no muta datos., setUpClass(), TokenizeTest

### Community 14 - "Community 14"
Cohesion: 0.2
Nodes (24): activate_bundle_version(), add_bundle_version(), bundle_by_catalog_item_id(), _clean(), create_bundle(), delete_bundle_version(), expand_quote_bundles(), get_active_bundle_version() (+16 more)

### Community 15 - "Community 15"
Cohesion: 0.15
Nodes (15): AdminFilterHelpersTest, AdminFilterRouteTest, Pruebas de filtros administrativos para proveedores y fichas., setUpClass(), filter_fichas(), filter_proveedores(), _indexed(), list_field_values() (+7 more)

### Community 16 - "Community 16"
Cohesion: 0.22
Nodes (12): ValidatorsTest, _clean(), _deleted_catalog_item_at(), _is_blank(), _parse_float(), _parse_ldm_items(), _parse_quote_items(), _validate_iso_date() (+4 more)

### Community 17 - "Community 17"
Cohesion: 0.17
Nodes (11): DeletionsTest, audit_deleted_catalog_items(), delete_catalog_items_data(), delete_project_data(), _mark_deleted_catalog_refs(), preserve_deleted_catalog_item_in_record(), purge_deleted_catalog_items_from_record(), Audit records for deleted catalog items and return summary statistics.      Args (+3 more)

### Community 18 - "Community 18"
Cohesion: 0.27
Nodes (13): filter_catalog(), _indexable_text(), list_categories(), match_item(), _normalize(), Búsqueda y filtrado del catálogo.  Funciones puras (sin I/O) para reutilizar ent, Quita acentos y baja a minúsculas para comparar texto en español., Divide la query en tokens normalizados, descartando vacíos. (+5 more)

### Community 19 - "Community 19"
Cohesion: 0.22
Nodes (2): BundleVersioningTest, ExpandQuoteBundlesTest

### Community 20 - "Community 20"
Cohesion: 0.31
Nodes (1): AdminFormsTest

### Community 21 - "Community 21"
Cohesion: 0.24
Nodes (3): AdminBundlesRoutesTest, Smoke tests de UI Admin para bundles y reglas COT/LDM., setUpClass()

### Community 22 - "Community 22"
Cohesion: 0.29
Nodes (1): ConversionRulesTest

### Community 23 - "Community 23"
Cohesion: 0.33
Nodes (2): ProjectDetailBundleUITest, Smoke tests for the bundle technical consistency UI in project_detail.html.

### Community 24 - "Community 24"
Cohesion: 0.38
Nodes (3): MaterialsCsvExportTest, Tests for exporting an existing LDM as CSV., setUpClass()

### Community 25 - "Community 25"
Cohesion: 0.47
Nodes (3): AuditDeletedCatalogRouteTest, Tests for the deleted catalog audit route., setUpClass()

### Community 26 - "Community 26"
Cohesion: 0.4
Nodes (2): QuoteCsvImportRouteTest, setUpClass()

### Community 27 - "Community 27"
Cohesion: 0.33
Nodes (1): ComparisonIgnoredTest

### Community 28 - "Community 28"
Cohesion: 0.5
Nodes (3): app.py, _is_truthy(), Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.

### Community 29 - "Community 29"
Cohesion: 0.67
Nodes (3): Flask Dependency, openpyxl Dependency, Tech Stack Declaration

### Community 30 - "Community 30"
Cohesion: 0.67
Nodes (1): fpdf2 Dependency

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (2): Data Integrity Rules (R1-R7), ProjectTracker System Rationale

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): graphify_detect.py

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): save_all_chunks.py

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): merge_extractions.py

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): save_chunks.py

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): graphify_cache.py

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): graphify_ast.py

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Roadmap Completed Features

## Knowledge Gaps
- **158 isolated node(s):** `graphify_detect.py`, `save_all_chunks.py`, `merge_extractions.py`, `save_chunks.py`, `graphify_cache.py` (+153 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 19`** (10 nodes): `BundleVersioningTest`, `.test_add_activate_and_delete_version()`, `.test_cannot_delete_only_version()`, `.test_create_bundle_has_active_v1()`, `ExpandQuoteBundlesTest`, `.test_expands_quote_bundle_components()`, `.test_seeded_circuit_bundles_expand_catalog_materials()`, `.test_unmapped_quote_items_are_preserved()`, `test_bundles.py`, `test_bundles.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (10 nodes): `AdminFormsTest`, `.assert_invalid_form_preserved()`, `.setUp()`, `.test_catalogo_invalid_form_preserves_capture()`, `.test_fichas_invalid_form_preserves_capture()`, `.test_proveedores_invalid_form_preserves_capture()`, `.test_settings_invalid_path_preserves_capture()`, `.test_team_invalid_form_preserves_capture()`, `test_admin_forms.py`, `test_admin_forms.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (7 nodes): `ConversionRulesTest`, `.test_aggregate_ldm_converts_to_expected_id()`, `.test_compare_expected_vs_actual_marks_shortage_and_excess()`, `.test_ldm_piece_to_cot_linear_meter()`, `.test_tolerance_accepts_small_differences()`, `test_comparison_rules.py`, `test_comparison_rules.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (7 nodes): `ProjectDetailBundleUITest`, `.test_materials_tab_exposes_csv_export_for_existing_ldms()`, `.test_materials_tab_exposes_partial_bundle_sync()`, `.test_template_contains_bundle_technical_consistency_section()`, `test_project_detail_bundle_ui.py`, `Smoke tests for the bundle technical consistency UI in project_detail.html.`, `test_project_detail_bundle_ui.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (6 nodes): `test_quote_csv_import_route.py`, `QuoteCsvImportRouteTest`, `._fake_load()`, `.test_import_quote_csv_renders_editable_preview()`, `setUpClass()`, `test_quote_csv_import_route.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (6 nodes): `ComparisonIgnoredTest`, `.test_filters_by_scope_and_active()`, `.test_split_ignored_linked()`, `.test_summarize_ignored()`, `test_comparison_ignored.py`, `test_comparison_ignored.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (3 nodes): `pdfs.py build_ldm_pdf()`, `pdfs.py build_quote_pdf()`, `fpdf2 Dependency`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (2 nodes): `Data Integrity Rules (R1-R7)`, `ProjectTracker System Rationale`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `graphify_detect.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `save_all_chunks.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `merge_extractions.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `save_chunks.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `graphify_cache.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `graphify_ast.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `Roadmap Completed Features`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load()` connect `Community 1` to `Community 0`, `Community 2`, `Community 8`, `Community 9`, `Community 11`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `parse_quote_csv()` connect `Community 5` to `Community 2`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `parse_ldm_csv()` connect `Community 7` to `Community 11`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 108 inferred relationships involving `load()` (e.g. with `migrate_catalog_fields()` and `catalog_description_lookup()`) actually correct?**
  _`load()` has 108 INFERRED edges - model-reasoned connections that need verification._
- **Are the 74 inferred relationships involving `save()` (e.g. with `migrate_catalog_fields()` and `migrate_task_statuses()`) actually correct?**
  _`save()` has 74 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `today()` (e.g. with `next_quote_number()` and `build_scope_task()`) actually correct?**
  _`today()` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `parse_quote_csv()` (e.g. with `.test_parse_quote_csv_reads_items_metadata_and_links_catalog()` and `.test_parse_quote_csv_accepts_spanish_headers_semicolon_and_missing_price()`) actually correct?**
  _`parse_quote_csv()` has 12 INFERRED edges - model-reasoned connections that need verification._