# Graph Report - .  (2026-05-03)

## Corpus Check
- 10 files · ~50,000 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 731 nodes · 1656 edges · 27 communities detected
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 464 edges (avg confidence: 0.8)
- Token cost: 119,051 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Admin & Bundle CRUD Routes|Admin & Bundle CRUD Routes]]
- [[_COMMUNITY_Materials & LDM Routes|Materials & LDM Routes]]
- [[_COMMUNITY_Project & Delivery Routes|Project & Delivery Routes]]
- [[_COMMUNITY_UI Base Templates & JS|UI Base Templates & JS]]
- [[_COMMUNITY_Comparison Ignore Rules|Comparison Ignore Rules]]
- [[_COMMUNITY_Catalog API & Audit|Catalog API & Audit]]
- [[_COMMUNITY_Core Business Logic|Core Business Logic]]
- [[_COMMUNITY_Domain & Service Tests|Domain & Service Tests]]
- [[_COMMUNITY_Consistency Tests|Consistency Tests]]
- [[_COMMUNITY_Catalog Search Tests|Catalog Search Tests]]
- [[_COMMUNITY_Bundle Versioning|Bundle Versioning]]
- [[_COMMUNITY_Validator Tests|Validator Tests]]
- [[_COMMUNITY_CSV Import Tests|CSV Import Tests]]
- [[_COMMUNITY_PDFs & Catalog|PDFs & Catalog]]
- [[_COMMUNITY_Catalog Search API|Catalog Search API]]
- [[_COMMUNITY_Drive Integration|Drive Integration]]
- [[_COMMUNITY_Admin Form Tests|Admin Form Tests]]
- [[_COMMUNITY_Bundle Route Tests|Bundle Route Tests]]
- [[_COMMUNITY_Bundle Unit Tests|Bundle Unit Tests]]
- [[_COMMUNITY_Comparison Rule Tests|Comparison Rule Tests]]
- [[_COMMUNITY_Ignored Items Tests|Ignored Items Tests]]
- [[_COMMUNITY_Bundle UI Tests|Bundle UI Tests]]
- [[_COMMUNITY_Flask App Entry|Flask App Entry]]
- [[_COMMUNITY_PDF Generation|PDF Generation]]
- [[_COMMUNITY_Dependencies & Stack|Dependencies & Stack]]
- [[_COMMUNITY_Core Logic Docs|Core Logic Docs]]
- [[_COMMUNITY_Roadmap Completed|Roadmap Completed]]

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

### Community 0 - "Admin & Bundle CRUD Routes"
Cohesion: 0.07
Nodes (91): activate_bundle_version_route(), add_bundle_version_route(), add_comparison_ignored(), api_catalogo(), api_catalogo_add(), bulk_delete_catalogo(), bundles(), _catalog_by_id() (+83 more)

### Community 1 - "Materials & LDM Routes"
Cohesion: 0.05
Nodes (66): _attach_csv_item_metadata(), _clean_form_text(), _csv_already_imported(), _csv_item_lookup(), _csv_path_for_project(), edit_ldm(), _find_project(), _hydrate_import_items() (+58 more)

### Community 2 - "Project & Delivery Routes"
Cohesion: 0.06
Nodes (59): ldm_pdf(), _project_drive_folder(), _blank_project_form_state(), create_delivery(), create_drive_folder(), new_project(), Crea la carpeta Drive del proyecto si aún no existe., serve_project_file() (+51 more)

### Community 3 - "UI Base Templates & JS"
Cohesion: 0.04
Nodes (66): Inyeccion app_version via Context Processor, Status Badges CSS bs-* ps-* src-*, Bootstrap Icons 1.11.3 CDN, Bootstrap 5.3.2 CDN, JS confirmDelete y submitFormWithConfirm, Flash Messages Display, Base Layout Template base.html, Modal Confirmacion Destructiva #modalConfirmDelete (+58 more)

### Community 4 - "Comparison Ignore Rules"
Cohesion: 0.07
Nodes (50): active_ignored_items(), _clean(), ignored_catalog_ids(), ignored_catalog_map(), normalize_ignored_item(), Artículos ignorados en comparación COT/LDM.  Los artículos ignorados siguen form, Normaliza una regla de artículo ignorado., Devuelve reglas activas aplicables al scope solicitado. (+42 more)

### Community 5 - "Catalog API & Audit"
Cohesion: 0.08
Nodes (48): API Endpoint /api/catalogo/add, API Endpoint /api/catalogo/bulk-delete, API Endpoint /api/catalogo, Audit Deleted Catalog Template, Base Layout Template, Bundle Entity (COT Commercial Item + LDM Components), Bundles Template, Catalog Inline AJAX Edit Pattern (+40 more)

### Community 6 - "Core Business Logic"
Cohesion: 0.07
Nodes (39): catalog.py hydrate_quote/ldm(), CLAUDE.md Graphify Rules, consistency.py compute_consistency(), csv_import.py parse_ldm_csv(), CSV Import API Routes (Pending), Catálogo Data Structure, Cotización al Cliente (COT) Data Structure, Lista de Materiales (LDM) Data Structure (+31 more)

### Community 7 - "Domain & Service Tests"
Cohesion: 0.12
Nodes (15): IdFactory, ProjectServicesTest, check_blocked(), currency(), fdate(), get_progress(), today_short(), apply_task_status_change() (+7 more)

### Community 8 - "Consistency Tests"
Cohesion: 0.14
Nodes (13): AggregateLdmItemsTest, AggregateQuoteItemsTest, BundleConsistencyIntegrationTest, ClassifyMarginTest, CompareItemsTest, ComputeConsistencyTest, IgnoredItemsConsistencyTest, _l_item() (+5 more)

### Community 9 - "Catalog Search Tests"
Cohesion: 0.07
Nodes (7): ApiCatalogoTest, FilterCatalogTest, ListCategoriesTest, MatchItemTest, Pruebas para tracker.catalog_search y la API /api/catalogo., Smoke-test del endpoint JSON; no muta datos., TokenizeTest

### Community 10 - "Bundle Versioning"
Cohesion: 0.17
Nodes (24): activate_bundle_version(), add_bundle_version(), bundle_by_catalog_item_id(), _clean(), create_bundle(), delete_bundle_version(), expand_quote_bundles(), get_active_bundle_version() (+16 more)

### Community 11 - "Validator Tests"
Cohesion: 0.21
Nodes (12): ValidatorsTest, _clean(), _deleted_catalog_item_at(), _is_blank(), _parse_float(), _parse_ldm_items(), _parse_quote_items(), _validate_iso_date() (+4 more)

### Community 12 - "CSV Import Tests"
Cohesion: 0.18
Nodes (13): LdmCsvImportTest, _build_catalog_index(), _clean(), _detect_dialect(), _first_value(), _header_key(), _match_catalog(), _parse_float() (+5 more)

### Community 13 - "PDFs & Catalog"
Cohesion: 0.24
Nodes (18): catalog_description_lookup(), build_ldm_pdf(), build_quote_pdf(), format_date_long(), money_pdf(), note_lines(), quote_catalog_description(), quote_cover_copy() (+10 more)

### Community 14 - "Catalog Search API"
Cohesion: 0.18
Nodes (16): api_catalogo_categorias(), Lista única de categorías existentes (para datalists/filtros)., Lista única de categorías existentes (para datalists/filtros)., filter_catalog(), _indexable_text(), list_categories(), match_item(), _normalize() (+8 more)

### Community 15 - "Drive Integration"
Cohesion: 0.2
Nodes (7): clear_lazy_loader(), LazyFileLoader, Get file information for a single file, Load file information in parallel for better performance, Shutdown the thread pool, Shutdown and clear the lazy loader thread pool., Lazy loader for large files to avoid loading all file metadata at once

### Community 16 - "Admin Form Tests"
Cohesion: 0.36
Nodes (1): AdminFormsTest

### Community 17 - "Bundle Route Tests"
Cohesion: 0.22
Nodes (2): AdminBundlesRoutesTest, Smoke tests de UI Admin para bundles y reglas COT/LDM.

### Community 18 - "Bundle Unit Tests"
Cohesion: 0.25
Nodes (2): BundleVersioningTest, ExpandQuoteBundlesTest

### Community 19 - "Comparison Rule Tests"
Cohesion: 0.33
Nodes (1): ConversionRulesTest

### Community 20 - "Ignored Items Tests"
Cohesion: 0.4
Nodes (1): ComparisonIgnoredTest

### Community 21 - "Bundle UI Tests"
Cohesion: 0.5
Nodes (2): ProjectDetailBundleUITest, Smoke tests for the bundle technical consistency UI in project_detail.html.

### Community 22 - "Flask App Entry"
Cohesion: 0.67
Nodes (2): _is_truthy(), Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.

### Community 23 - "PDF Generation"
Cohesion: 0.67
Nodes (1): fpdf2 Dependency

### Community 24 - "Dependencies & Stack"
Cohesion: 0.67
Nodes (3): Flask Dependency, openpyxl Dependency, Tech Stack Declaration

### Community 25 - "Core Logic Docs"
Cohesion: 1.0
Nodes (2): Data Integrity Rules (R1-R7), ProjectTracker System Rationale

### Community 33 - "Roadmap Completed"
Cohesion: 1.0
Nodes (1): Roadmap Completed Features

## Knowledge Gaps
- **133 isolated node(s):** `Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.`, `Asegura que cada artículo tenga el campo `categoria` (default '').      Migració`, `Convierte cualquier valor a str limpio, apto para fpdf2 con DejaVu (UTF-8).`, `Registra las fuentes DejaVu guardadas en .codex_tmp/fonts/ del proyecto.     Dev`, `Genera el PDF de una Lista de Materiales con la estética del PDF de     cotizaci` (+128 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Admin Form Tests`** (9 nodes): `AdminFormsTest`, `.assert_invalid_form_preserved()`, `.setUp()`, `.test_catalogo_invalid_form_preserves_capture()`, `.test_fichas_invalid_form_preserves_capture()`, `.test_proveedores_invalid_form_preserves_capture()`, `.test_settings_invalid_path_preserves_capture()`, `.test_team_invalid_form_preserves_capture()`, `test_admin_forms.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Bundle Route Tests`** (9 nodes): `AdminBundlesRoutesTest`, `._fake_load()`, `.test_bundles_page_loads()`, `.test_comparison_rules_page_loads()`, `.test_create_bundle_persists_bundle()`, `.test_create_comparison_rule_persists_rule()`, `test_admin_bundles_routes.py`, `Smoke tests de UI Admin para bundles y reglas COT/LDM.`, `setUpClass()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Bundle Unit Tests`** (8 nodes): `BundleVersioningTest`, `.test_add_activate_and_delete_version()`, `.test_cannot_delete_only_version()`, `.test_create_bundle_has_active_v1()`, `ExpandQuoteBundlesTest`, `.test_expands_quote_bundle_components()`, `.test_unmapped_quote_items_are_preserved()`, `test_bundles.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Comparison Rule Tests`** (6 nodes): `ConversionRulesTest`, `.test_aggregate_ldm_converts_to_expected_id()`, `.test_compare_expected_vs_actual_marks_shortage_and_excess()`, `.test_ldm_piece_to_cot_linear_meter()`, `.test_tolerance_accepts_small_differences()`, `test_comparison_rules.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Ignored Items Tests`** (5 nodes): `ComparisonIgnoredTest`, `.test_filters_by_scope_and_active()`, `.test_split_ignored_linked()`, `.test_summarize_ignored()`, `test_comparison_ignored.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Bundle UI Tests`** (4 nodes): `ProjectDetailBundleUITest`, `.test_template_contains_bundle_technical_consistency_section()`, `test_project_detail_bundle_ui.py`, `Smoke tests for the bundle technical consistency UI in project_detail.html.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Flask App Entry`** (3 nodes): `app.py`, `_is_truthy()`, `Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `PDF Generation`** (3 nodes): `pdfs.py build_ldm_pdf()`, `pdfs.py build_quote_pdf()`, `fpdf2 Dependency`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Core Logic Docs`** (2 nodes): `Data Integrity Rules (R1-R7)`, `ProjectTracker System Rationale`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Roadmap Completed`** (1 nodes): `Roadmap Completed Features`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load()` connect `Admin & Bundle CRUD Routes` to `Materials & LDM Routes`, `Project & Delivery Routes`, `Domain & Service Tests`, `PDFs & Catalog`, `Catalog Search API`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `save()` connect `Admin & Bundle CRUD Routes` to `Materials & LDM Routes`, `Project & Delivery Routes`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `today()` connect `Admin & Bundle CRUD Routes` to `Materials & LDM Routes`, `Project & Delivery Routes`, `Domain & Service Tests`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 103 inferred relationships involving `load()` (e.g. with `migrate_catalog_fields()` and `catalog_description_lookup()`) actually correct?**
  _`load()` has 103 INFERRED edges - model-reasoned connections that need verification._
- **Are the 73 inferred relationships involving `save()` (e.g. with `migrate_catalog_fields()` and `migrate_task_statuses()`) actually correct?**
  _`save()` has 73 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `today()` (e.g. with `next_quote_number()` and `build_scope_task()`) actually correct?**
  _`today()` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `active_drive_paths()` (e.g. with `build_project_detail_context()` and `new_project()`) actually correct?**
  _`active_drive_paths()` has 15 INFERRED edges - model-reasoned connections that need verification._