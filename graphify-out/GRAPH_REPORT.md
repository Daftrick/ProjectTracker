# Graph Report - ProjectTracker  (2026-05-28)

## Corpus Check
- 54 files · ~86,421 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1099 nodes · 2669 edges · 38 communities detected
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 555 edges (avg confidence: 0.8)
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
- [[_COMMUNITY_Community 51|Community 51]]

## God Nodes (most connected - your core abstractions)
1. `load()` - 116 edges
2. `save()` - 79 edges
3. `today()` - 42 edges
4. `compute_consistency()` - 28 edges
5. `build_project_detail_context()` - 27 edges
6. `parse_quote_csv()` - 26 edges
7. `catalog_maps()` - 25 edges
8. `active_drive_paths()` - 23 edges
9. `parse_ldm_csv()` - 21 edges
10. `load_config()` - 19 edges

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
Cohesion: 0.04
Nodes (84): ldm_pdf(), create_drive_folder(), Crea la carpeta Drive del proyecto si aún no existe., Crea la carpeta Drive del proyecto si aún no existe., serve_project_file(), settings(), _settings_view_config(), quote_pdf() (+76 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (92): activate_bundle_version_route(), add_bundle_version_route(), add_comparison_ignored(), api_catalogo(), api_catalogo_add(), api_catalogo_categorias(), api_catalogo_impact(), bulk_delete_catalogo() (+84 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (75): dashboard(), audit_deleted_catalog(), _build_quote_workbook(), delete_quote(), edit_quote(), _find_project(), import_quote_csv(), import_quote_csv_drive() (+67 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (66): Inyeccion app_version via Context Processor, Status Badges CSS bs-* ps-* src-*, Bootstrap Icons 1.11.3 CDN, Bootstrap 5.3.2 CDN, JS confirmDelete y submitFormWithConfirm, Flash Messages Display, Base Layout Template base.html, Modal Confirmacion Destructiva #modalConfirmDelete (+58 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (55): approve_quote(), is_base_quote_type(), quote_type_key(), Generales y Preliminares compiten entre sí; Extraordinarias son independientes., Marca la cotización target_id como active.      Si es General/Preliminar, pasa l, active_ignored_items(), _clean(), ignored_catalog_ids() (+47 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (25): QuoteCsvImportTest, QuoteSymbolFixturesTest, CSV escrito en cp1252 (fallback ANSI del LISP) debe retornar error         legib, CSV escrito en cp1252 (fallback ANSI del LISP) debe retornar error         legib, CotTubeFixturesTest, Tests parametrizados para importación CSV de tubería conduit.  Cubre los 6 tipos, Metadata #proyecto_clave y #quote_type del archivo COT LISP., Múltiples tipos y diámetros en un solo archivo COT. (+17 more)

### Community 6 - "Community 6"
Cohesion: 0.1
Nodes (42): api_ldm_set_costo(), _attach_csv_item_metadata(), _bundle_suggestion_ldm(), _clean_form_text(), _clear_pdf_import(), _csv_already_imported(), _csv_item_lookup(), _csv_number() (+34 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (48): API Endpoint /api/catalogo/add, API Endpoint /api/catalogo/bulk-delete, API Endpoint /api/catalogo, Audit Deleted Catalog Template, Base Layout Template, Bundle Entity (COT Commercial Item + LDM Components), Bundles Template, Catalog Inline AJAX Edit Pattern (+40 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (21): LdmCsvImportTest, CSV escrito en cp1252 (fallback ANSI del LISP) debe retornar error         legib, LdmTubeFixturesTest, Múltiples tipos de tubería en un mismo archivo LDM., Metadata #proveedor y #fecha post-header (formato real del LISP)., Escribe un CSV LDM con header estándar y filas dadas.      meta_rows: lista de t, _write_ldm(), _build_catalog_index() (+13 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (32): ProjectViewTest, check_blocked(), currency(), fdate(), get_progress(), today_short(), _as_float(), build_consistency_view() (+24 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (39): catalog.py hydrate_quote/ldm(), CLAUDE.md Graphify Rules, consistency.py compute_consistency(), csv_import.py parse_ldm_csv(), CSV Import API Routes (Pending), Catálogo Data Structure, Cotización al Cliente (COT) Data Structure, Lista de Materiales (LDM) Data Structure (+31 more)

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (16): AggregateLdmItemsTest, AggregateQuoteItemsTest, BundleConsistencyIntegrationTest, ClassifyMarginTest, CompareItemsTest, ComputeConsistencyTest, IgnoredItemsConsistencyTest, _l_item() (+8 more)

### Community 12 - "Community 12"
Cohesion: 0.11
Nodes (29): LdmSyncTest, MaterialsSyncRouteTest, Pruebas de sincronizacion parcial LDM desde bundles., setUpClass(), active_rules(), aggregate_ldm_for_expected_items(), apply_rounding(), _clean() (+21 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (32): activate_bundle_version(), add_bundle_version(), bundle_by_catalog_item_id(), _clean(), create_bundle(), delete_bundle_version(), expand_quote_bundles(), get_active_bundle_version() (+24 more)

### Community 14 - "Community 14"
Cohesion: 0.08
Nodes (8): ApiCatalogoTest, FilterCatalogTest, ListCategoriesTest, MatchItemTest, Pruebas para tracker.catalog_search y la API /api/catalogo., Smoke-test del endpoint JSON; no muta datos., setUpClass(), TokenizeTest

### Community 15 - "Community 15"
Cohesion: 0.17
Nodes (11): IdFactory, ProjectServicesTest, apply_task_status_change(), build_checklist_items(), build_edited_checklist_items(), build_scope_task(), create_project_with_tasks(), next_folder_number() (+3 more)

### Community 16 - "Community 16"
Cohesion: 0.22
Nodes (12): ValidatorsTest, _clean(), _deleted_catalog_item_at(), _is_blank(), _parse_float(), _parse_ldm_items(), _parse_quote_items(), _validate_iso_date() (+4 more)

### Community 17 - "Community 17"
Cohesion: 0.15
Nodes (15): AdminFilterHelpersTest, AdminFilterRouteTest, Pruebas de filtros administrativos para proveedores y fichas., setUpClass(), filter_fichas(), filter_proveedores(), _indexed(), list_field_values() (+7 more)

### Community 18 - "Community 18"
Cohesion: 0.31
Nodes (17): build_ldm_pdf(), build_quote_pdf(), format_date_long(), money_pdf(), note_lines(), quote_catalog_description(), quote_cover_copy(), quote_logo_path() (+9 more)

### Community 19 - "Community 19"
Cohesion: 0.27
Nodes (13): filter_catalog(), _indexable_text(), list_categories(), match_item(), _normalize(), Búsqueda y filtrado del catálogo.  Funciones puras (sin I/O) para reutilizar ent, Quita acentos y baja a minúsculas para comparar texto en español., Divide la query en tokens normalizados, descartando vacíos. (+5 more)

### Community 20 - "Community 20"
Cohesion: 0.27
Nodes (13): _clean(), _extract_from_tables(), _extract_from_text(), extract_items_from_pdf(), _extract_procables(), _extract_procables_meta(), _header_map(), _is_procables() (+5 more)

### Community 21 - "Community 21"
Cohesion: 0.17
Nodes (2): CsvCotFilenameTest, Tests para parse_csv_cot_filename y decorate_csv_cot.

### Community 22 - "Community 22"
Cohesion: 0.22
Nodes (3): AdminBundlesRoutesTest, Smoke tests de UI Admin para bundles., setUpClass()

### Community 23 - "Community 23"
Cohesion: 0.31
Nodes (1): AdminFormsTest

### Community 24 - "Community 24"
Cohesion: 0.22
Nodes (2): BundleVersioningTest, ExpandQuoteBundlesTest

### Community 25 - "Community 25"
Cohesion: 0.25
Nodes (2): ProjectDetailBundleUITest, Smoke tests for simplified project detail COT/LDM UI.

### Community 26 - "Community 26"
Cohesion: 0.38
Nodes (3): MaterialsCsvExportTest, Tests for exporting an existing LDM as CSV., setUpClass()

### Community 27 - "Community 27"
Cohesion: 0.29
Nodes (1): ConversionRulesTest

### Community 28 - "Community 28"
Cohesion: 0.47
Nodes (3): AuditDeletedCatalogRouteTest, Tests for the deleted catalog audit route., setUpClass()

### Community 29 - "Community 29"
Cohesion: 0.4
Nodes (2): QuoteCsvImportRouteTest, setUpClass()

### Community 30 - "Community 30"
Cohesion: 0.33
Nodes (1): LdmPdfImportRoutesTest

### Community 31 - "Community 31"
Cohesion: 0.33
Nodes (1): ComparisonIgnoredTest

### Community 32 - "Community 32"
Cohesion: 0.5
Nodes (2): _is_truthy(), Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.

### Community 33 - "Community 33"
Cohesion: 0.67
Nodes (3): iter_python_files(), main(), Parse project Python files without writing bytecode.

### Community 34 - "Community 34"
Cohesion: 0.67
Nodes (3): Flask Dependency, openpyxl Dependency, Tech Stack Declaration

### Community 35 - "Community 35"
Cohesion: 0.67
Nodes (1): fpdf2 Dependency

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (2): Data Integrity Rules (R1-R7), ProjectTracker System Rationale

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Roadmap Completed Features

## Knowledge Gaps
- **213 isolated node(s):** `Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.`, `Asegura que cada artículo tenga el campo `categoria` (default '').      Migració`, `Generales y Preliminares compiten entre sí; Extraordinarias son independientes.`, `Migración idempotente: asigna approval_status a cotizaciones que no lo tienen.`, `Marca la cotización target_id como active.      Si es General/Preliminar, pasa l` (+208 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 21`** (12 nodes): `CsvCotFilenameTest`, `.setUp()`, `.test_case_insensitive()`, `.test_decorate_marks_desactualizado_when_newer_exists()`, `.test_decorate_marks_importado_when_linked()`, `.test_decorate_marks_pending_unlinked()`, `.test_parses_valid_cot_csv()`, `.test_rejects_ldm_csv()`, `.test_rejects_wrong_clave()`, `.test_version_key_invalid_returns_sentinel()`, `.test_version_key_ordering()`, `Tests para parse_csv_cot_filename y decorate_csv_cot.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (10 nodes): `AdminFormsTest`, `.assert_invalid_form_preserved()`, `.setUp()`, `.test_catalogo_invalid_form_preserves_capture()`, `.test_fichas_invalid_form_preserves_capture()`, `.test_proveedores_invalid_form_preserves_capture()`, `.test_settings_invalid_path_preserves_capture()`, `.test_team_invalid_form_preserves_capture()`, `test_admin_forms.py`, `test_admin_forms.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (10 nodes): `BundleVersioningTest`, `.test_add_activate_and_delete_version()`, `.test_cannot_delete_only_version()`, `.test_create_bundle_has_active_v1()`, `ExpandQuoteBundlesTest`, `.test_expands_quote_bundle_components()`, `.test_seeded_circuit_bundles_expand_catalog_materials()`, `.test_unmapped_quote_items_are_preserved()`, `test_bundles.py`, `test_bundles.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (9 nodes): `ProjectDetailBundleUITest`, `.test_materials_tab_exposes_csv_export_for_existing_ldms()`, `.test_materials_tab_exposes_partial_bundle_sync()`, `.test_materials_tab_hides_partial_bundle_sync()`, `.test_template_contains_bundle_technical_consistency_section()`, `.test_template_contains_simple_cot_ldm_summary()`, `test_project_detail_bundle_ui.py`, `Smoke tests for simplified project detail COT/LDM UI.`, `test_project_detail_bundle_ui.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (7 nodes): `ConversionRulesTest`, `.test_aggregate_ldm_converts_to_expected_id()`, `.test_compare_expected_vs_actual_marks_shortage_and_excess()`, `.test_ldm_piece_to_cot_linear_meter()`, `.test_tolerance_accepts_small_differences()`, `test_comparison_rules.py`, `test_comparison_rules.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (6 nodes): `test_quote_csv_import_route.py`, `QuoteCsvImportRouteTest`, `._fake_load()`, `.test_import_quote_csv_renders_editable_preview()`, `setUpClass()`, `test_quote_csv_import_route.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (6 nodes): `LdmPdfImportRoutesTest`, `.test_create_pdf_import_is_blocked_when_project_is_closed()`, `.test_upload_pdf_is_blocked_when_project_is_closed()`, `.test_upload_stores_pdf_import_payload_outside_cookie_session()`, `test_ldm_pdf_import_routes.py`, `setUpClass()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (6 nodes): `ComparisonIgnoredTest`, `.test_filters_by_scope_and_active()`, `.test_split_ignored_linked()`, `.test_summarize_ignored()`, `test_comparison_ignored.py`, `test_comparison_ignored.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (4 nodes): `app.py`, `app.py`, `_is_truthy()`, `Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (3 nodes): `pdfs.py build_ldm_pdf()`, `pdfs.py build_quote_pdf()`, `fpdf2 Dependency`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (2 nodes): `Data Integrity Rules (R1-R7)`, `ProjectTracker System Rationale`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Roadmap Completed Features`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load()` connect `Community 1` to `Community 0`, `Community 9`, `Community 2`, `Community 6`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `parse_ldm_csv()` connect `Community 8` to `Community 6`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `import_ldm_csv()` connect `Community 6` to `Community 8`, `Community 1`, `Community 16`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 114 inferred relationships involving `load()` (e.g. with `migrate_catalog_fields()` and `catalog_description_lookup()`) actually correct?**
  _`load()` has 114 INFERRED edges - model-reasoned connections that need verification._
- **Are the 77 inferred relationships involving `save()` (e.g. with `migrate_catalog_fields()` and `_migrate_quote_approval()`) actually correct?**
  _`save()` has 77 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `today()` (e.g. with `next_quote_number()` and `build_scope_task()`) actually correct?**
  _`today()` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `compute_consistency()` (e.g. with `build_project_detail_context()` and `quote_type_key()`) actually correct?**
  _`compute_consistency()` has 10 INFERRED edges - model-reasoned connections that need verification._