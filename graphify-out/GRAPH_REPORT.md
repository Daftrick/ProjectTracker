# Graph Report - .  (2026-05-03)

## Corpus Check
- 75 files · ~75,337 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 661 nodes · 1515 edges · 28 communities detected
- Extraction: 70% EXTRACTED · 30% INFERRED · 0% AMBIGUOUS · INFERRED: 458 edges (avg confidence: 0.8)
- Token cost: 14,800 input · 2,900 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Admin, Project & Quote Routes|Admin, Project & Quote Routes]]
- [[_COMMUNITY_Drive, Config & Project Setup|Drive, Config & Project Setup]]
- [[_COMMUNITY_Document Generation & Catalog|Document Generation & Catalog]]
- [[_COMMUNITY_UI Templates & Domain Entities|UI Templates & Domain Entities]]
- [[_COMMUNITY_Docs & Architecture Notes|Docs & Architecture Notes]]
- [[_COMMUNITY_COTLDM Consistency Engine|COT/LDM Consistency Engine]]
- [[_COMMUNITY_Consistency Test Suite|Consistency Test Suite]]
- [[_COMMUNITY_Catalog Search Tests|Catalog Search Tests]]
- [[_COMMUNITY_Bundle Versioning System|Bundle Versioning System]]
- [[_COMMUNITY_LDM Import & Form Models|LDM Import & Form Models]]
- [[_COMMUNITY_Project Services & Task Logic|Project Services & Task Logic]]
- [[_COMMUNITY_Form Validators|Form Validators]]
- [[_COMMUNITY_CSV Import Parser|CSV Import Parser]]
- [[_COMMUNITY_Comparison Rules Engine|Comparison Rules Engine]]
- [[_COMMUNITY_Catalog Search Engine|Catalog Search Engine]]
- [[_COMMUNITY_Lazy File Loader|Lazy File Loader]]
- [[_COMMUNITY_Admin Forms Tests|Admin Forms Tests]]
- [[_COMMUNITY_Bundle Routes Tests|Bundle Routes Tests]]
- [[_COMMUNITY_Bundle Versioning Tests|Bundle Versioning Tests]]
- [[_COMMUNITY_Comparison Rules Tests|Comparison Rules Tests]]
- [[_COMMUNITY_Comparison Ignored Tests|Comparison Ignored Tests]]
- [[_COMMUNITY_Deleted Catalog Audit|Deleted Catalog Audit]]
- [[_COMMUNITY_Bundle UI Tests|Bundle UI Tests]]
- [[_COMMUNITY_App Entry Point|App Entry Point]]
- [[_COMMUNITY_PDF Builder|PDF Builder]]
- [[_COMMUNITY_Flask Stack Dependencies|Flask Stack Dependencies]]
- [[_COMMUNITY_Data Integrity Rules|Data Integrity Rules]]
- [[_COMMUNITY_Completed Roadmap Items|Completed Roadmap Items]]

## God Nodes (most connected - your core abstractions)
1. `load()` - 104 edges
2. `save()` - 74 edges
3. `today()` - 37 edges
4. `active_drive_paths()` - 21 edges
5. `compute_consistency()` - 20 edges
6. `catalog_maps()` - 18 edges
7. `load_config()` - 17 edges
8. `build_project_detail_context()` - 17 edges
9. `Quote Project Form Template (Advanced)` - 17 edges
10. `parse_ldm_csv()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Catalog Hydration Logic` --semantically_similar_to--> `Consistency COT vs LDM Module`  [INFERRED] [semantically similar]
  logica_cuantificaciones.txt → VERSIONES.md
- `materials.py import_ldm_csv route` --implements--> `Lista de Materiales (LDM) Data Structure`  [INFERRED]
  tracker/routes/materials.py → REFERENCIA_ESTRUCTURAS_CSV.txt
- `CSV→LDM Import Diff Algorithm` --rationale_for--> `csv_import.py parse_ldm_csv()`  [INFERRED]
  logica_cuantificaciones.txt → tracker/csv_import.py
- `CSV→LDM Import Diff Algorithm` --rationale_for--> `materials.py import_ldm_csv route`  [INFERRED]
  logica_cuantificaciones.txt → tracker/routes/materials.py
- `CSV→LDM Import Diff Algorithm` --semantically_similar_to--> `Deleted Catalog Audit System`  [INFERRED] [semantically similar]
  logica_cuantificaciones.txt → VERSIONES.md

## Hyperedges (group relationships)
- **AutoCAD/LISP → CSV → App Import Pipeline** — csv_ref_workflow_lisp, logica_csv_plano, csv_import_py_parse, routes_materials_import, csv_ref_ldm [EXTRACTED 0.95]
- **COT / LDM / Catalog Consistency Check** — csv_ref_cot, csv_ref_ldm, csv_ref_catalogo, consistency_py_compute, versiones_consistency_module [EXTRACTED 0.95]
- **Project + Drive Folder + File Naming Convention** — logica_proyecto_entity, naming_drive_folder, versiones_drive_integration, drive_scan_folder_fn [EXTRACTED 0.90]
- **COT/LDM Technical Consistency System** — bundle_entity, comparison_rule_entity, comparison_ignored_entity, ldm_entity, quote_entity [INFERRED 0.85]
- **Catalog Item Lifecycle (Create/Edit/Delete/Audit)** — catalog_item_entity, catalogo_template, deleted_catalog_item_pattern, audit_deleted_catalog_template [EXTRACTED 0.95]
- **Quote Form UX Patterns (Drag, Filter, Autocomplete, Fixed Bar, Sticky Header)** — drag_reorder_rows_pattern, partida_filter_pattern, inline_autocomplete_catalog_pattern, fixed_bottom_bar_pattern, sticky_table_header_pattern [INFERRED 0.85]

## Communities

### Community 0 - "Admin, Project & Quote Routes"
Cohesion: 0.06
Nodes (100): activate_bundle_version_route(), add_bundle_version_route(), add_comparison_ignored(), api_catalogo(), api_catalogo_add(), api_catalogo_categorias(), bulk_delete_catalogo(), bundles() (+92 more)

### Community 1 - "Drive, Config & Project Setup"
Cohesion: 0.05
Nodes (64): ldm_pdf(), _project_drive_folder(), _blank_project_form_state(), create_delivery(), create_drive_folder(), new_project(), Crea la carpeta Drive del proyecto si aún no existe., serve_project_file() (+56 more)

### Community 2 - "Document Generation & Catalog"
Cohesion: 0.07
Nodes (51): purge_ldm_deleted_catalog_items(), dashboard(), _build_quote_workbook(), edit_quote(), purge_deleted_item(), purge_quote_deleted_catalog_items(), quote_pdf(), Construye el workbook Excel de la cotización.      Devuelve (wb, filename) para (+43 more)

### Community 3 - "UI Templates & Domain Entities"
Cohesion: 0.08
Nodes (48): API Endpoint /api/catalogo/add, API Endpoint /api/catalogo/bulk-delete, API Endpoint /api/catalogo, Audit Deleted Catalog Template, Base Layout Template, Bundle Entity (COT Commercial Item + LDM Components), Bundles Template, Catalog Inline AJAX Edit Pattern (+40 more)

### Community 4 - "Docs & Architecture Notes"
Cohesion: 0.07
Nodes (39): catalog.py hydrate_quote/ldm(), CLAUDE.md Graphify Rules, consistency.py compute_consistency(), csv_import.py parse_ldm_csv(), CSV Import API Routes (Pending), Catálogo Data Structure, Cotización al Cliente (COT) Data Structure, Lista de Materiales (LDM) Data Structure (+31 more)

### Community 5 - "COT/LDM Consistency Engine"
Cohesion: 0.09
Nodes (36): active_ignored_items(), _clean(), ignored_catalog_ids(), ignored_catalog_map(), normalize_ignored_item(), Artículos ignorados en comparación COT/LDM.  Los artículos ignorados siguen form, Normaliza una regla de artículo ignorado., Devuelve reglas activas aplicables al scope solicitado. (+28 more)

### Community 6 - "Consistency Test Suite"
Cohesion: 0.14
Nodes (13): AggregateLdmItemsTest, AggregateQuoteItemsTest, BundleConsistencyIntegrationTest, ClassifyMarginTest, CompareItemsTest, ComputeConsistencyTest, IgnoredItemsConsistencyTest, _l_item() (+5 more)

### Community 7 - "Catalog Search Tests"
Cohesion: 0.07
Nodes (7): ApiCatalogoTest, FilterCatalogTest, ListCategoriesTest, MatchItemTest, Pruebas para tracker.catalog_search y la API /api/catalogo., Smoke-test del endpoint JSON; no muta datos., TokenizeTest

### Community 8 - "Bundle Versioning System"
Cohesion: 0.17
Nodes (24): activate_bundle_version(), add_bundle_version(), bundle_by_catalog_item_id(), _clean(), create_bundle(), delete_bundle_version(), expand_quote_bundles(), get_active_bundle_version() (+16 more)

### Community 9 - "LDM Import & Form Models"
Cohesion: 0.16
Nodes (18): _attach_csv_item_metadata(), _clean_form_text(), _csv_already_imported(), _csv_item_lookup(), _csv_path_for_project(), edit_ldm(), _find_project(), _hydrate_import_items() (+10 more)

### Community 10 - "Project Services & Task Logic"
Cohesion: 0.15
Nodes (11): IdFactory, ProjectServicesTest, check_blocked(), apply_task_status_change(), build_checklist_items(), build_edited_checklist_items(), build_scope_task(), create_project_with_tasks() (+3 more)

### Community 11 - "Form Validators"
Cohesion: 0.21
Nodes (12): ValidatorsTest, _clean(), _deleted_catalog_item_at(), _is_blank(), _parse_float(), _parse_ldm_items(), _parse_quote_items(), _validate_iso_date() (+4 more)

### Community 12 - "CSV Import Parser"
Cohesion: 0.18
Nodes (13): LdmCsvImportTest, _build_catalog_index(), _clean(), _detect_dialect(), _first_value(), _header_key(), _match_catalog(), _parse_float() (+5 more)

### Community 13 - "Comparison Rules Engine"
Cohesion: 0.28
Nodes (14): active_rules(), aggregate_ldm_for_expected_items(), apply_rounding(), _clean(), compare_expected_vs_actual(), convert_qty(), normalize_rule(), Reglas de comparación entre COT y LDM.  Permiten relacionar artículos equivalent (+6 more)

### Community 14 - "Catalog Search Engine"
Cohesion: 0.23
Nodes (13): filter_catalog(), _indexable_text(), list_categories(), match_item(), _normalize(), Búsqueda y filtrado del catálogo.  Funciones puras (sin I/O) para reutilizar ent, Quita acentos y baja a minúsculas para comparar texto en español., Divide la query en tokens normalizados, descartando vacíos. (+5 more)

### Community 15 - "Lazy File Loader"
Cohesion: 0.2
Nodes (7): clear_lazy_loader(), LazyFileLoader, Get file information for a single file, Load file information in parallel for better performance, Shutdown the thread pool, Shutdown and clear the lazy loader thread pool., Lazy loader for large files to avoid loading all file metadata at once

### Community 16 - "Admin Forms Tests"
Cohesion: 0.36
Nodes (1): AdminFormsTest

### Community 17 - "Bundle Routes Tests"
Cohesion: 0.22
Nodes (2): AdminBundlesRoutesTest, Smoke tests de UI Admin para bundles y reglas COT/LDM.

### Community 18 - "Bundle Versioning Tests"
Cohesion: 0.25
Nodes (2): BundleVersioningTest, ExpandQuoteBundlesTest

### Community 19 - "Comparison Rules Tests"
Cohesion: 0.33
Nodes (1): ConversionRulesTest

### Community 20 - "Comparison Ignored Tests"
Cohesion: 0.4
Nodes (1): ComparisonIgnoredTest

### Community 21 - "Deleted Catalog Audit"
Cohesion: 0.5
Nodes (4): audit_deleted_catalog(), Audit all quotes and LDMs for deleted catalog items, audit_deleted_catalog_items(), Audit records for deleted catalog items and return summary statistics.      Args

### Community 22 - "Bundle UI Tests"
Cohesion: 0.5
Nodes (2): ProjectDetailBundleUITest, Smoke tests for the bundle technical consistency UI in project_detail.html.

### Community 23 - "App Entry Point"
Cohesion: 0.67
Nodes (2): _is_truthy(), Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.

### Community 24 - "PDF Builder"
Cohesion: 0.67
Nodes (1): fpdf2 Dependency

### Community 25 - "Flask Stack Dependencies"
Cohesion: 0.67
Nodes (3): Flask Dependency, openpyxl Dependency, Tech Stack Declaration

### Community 26 - "Data Integrity Rules"
Cohesion: 1.0
Nodes (2): Data Integrity Rules (R1-R7), ProjectTracker System Rationale

### Community 34 - "Completed Roadmap Items"
Cohesion: 1.0
Nodes (1): Roadmap Completed Features

## Knowledge Gaps
- **102 isolated node(s):** `Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.`, `Asegura que cada artículo tenga el campo `categoria` (default '').      Migració`, `Convierte cualquier valor a str limpio, apto para fpdf2 con DejaVu (UTF-8).`, `Registra las fuentes DejaVu guardadas en .codex_tmp/fonts/ del proyecto.     Dev`, `Genera el PDF de una Lista de Materiales con la estética del PDF de     cotizaci` (+97 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Admin Forms Tests`** (9 nodes): `AdminFormsTest`, `.assert_invalid_form_preserved()`, `.setUp()`, `.test_catalogo_invalid_form_preserves_capture()`, `.test_fichas_invalid_form_preserves_capture()`, `.test_proveedores_invalid_form_preserves_capture()`, `.test_settings_invalid_path_preserves_capture()`, `.test_team_invalid_form_preserves_capture()`, `test_admin_forms.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Bundle Routes Tests`** (9 nodes): `AdminBundlesRoutesTest`, `._fake_load()`, `.test_bundles_page_loads()`, `.test_comparison_rules_page_loads()`, `.test_create_bundle_persists_bundle()`, `.test_create_comparison_rule_persists_rule()`, `test_admin_bundles_routes.py`, `Smoke tests de UI Admin para bundles y reglas COT/LDM.`, `setUpClass()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Bundle Versioning Tests`** (8 nodes): `BundleVersioningTest`, `.test_add_activate_and_delete_version()`, `.test_cannot_delete_only_version()`, `.test_create_bundle_has_active_v1()`, `ExpandQuoteBundlesTest`, `.test_expands_quote_bundle_components()`, `.test_unmapped_quote_items_are_preserved()`, `test_bundles.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Comparison Rules Tests`** (6 nodes): `ConversionRulesTest`, `.test_aggregate_ldm_converts_to_expected_id()`, `.test_compare_expected_vs_actual_marks_shortage_and_excess()`, `.test_ldm_piece_to_cot_linear_meter()`, `.test_tolerance_accepts_small_differences()`, `test_comparison_rules.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Comparison Ignored Tests`** (5 nodes): `ComparisonIgnoredTest`, `.test_filters_by_scope_and_active()`, `.test_split_ignored_linked()`, `.test_summarize_ignored()`, `test_comparison_ignored.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Bundle UI Tests`** (4 nodes): `ProjectDetailBundleUITest`, `.test_template_contains_bundle_technical_consistency_section()`, `test_project_detail_bundle_ui.py`, `Smoke tests for the bundle technical consistency UI in project_detail.html.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `App Entry Point`** (3 nodes): `app.py`, `_is_truthy()`, `Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `PDF Builder`** (3 nodes): `pdfs.py build_ldm_pdf()`, `pdfs.py build_quote_pdf()`, `fpdf2 Dependency`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Data Integrity Rules`** (2 nodes): `Data Integrity Rules (R1-R7)`, `ProjectTracker System Rationale`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Completed Roadmap Items`** (1 nodes): `Roadmap Completed Features`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load()` connect `Admin, Project & Quote Routes` to `Drive, Config & Project Setup`, `Document Generation & Catalog`, `Deleted Catalog Audit`, `LDM Import & Form Models`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `save()` connect `Admin, Project & Quote Routes` to `Drive, Config & Project Setup`, `Document Generation & Catalog`, `LDM Import & Form Models`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `today()` connect `Admin, Project & Quote Routes` to `Drive, Config & Project Setup`, `Document Generation & Catalog`, `Project Services & Task Logic`, `LDM Import & Form Models`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 103 inferred relationships involving `load()` (e.g. with `migrate_catalog_fields()` and `catalog_description_lookup()`) actually correct?**
  _`load()` has 103 INFERRED edges - model-reasoned connections that need verification._
- **Are the 73 inferred relationships involving `save()` (e.g. with `migrate_catalog_fields()` and `migrate_task_statuses()`) actually correct?**
  _`save()` has 73 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `today()` (e.g. with `next_quote_number()` and `build_scope_task()`) actually correct?**
  _`today()` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `active_drive_paths()` (e.g. with `build_project_detail_context()` and `new_project()`) actually correct?**
  _`active_drive_paths()` has 15 INFERRED edges - model-reasoned connections that need verification._