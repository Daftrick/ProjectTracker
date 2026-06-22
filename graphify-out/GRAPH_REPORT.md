# Graph Report - ProjectTracker  (2026-06-21)

## Corpus Check
- 70 files · ~103,154 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1486 nodes · 3657 edges · 45 communities detected
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 728 edges (avg confidence: 0.8)
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
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 60|Community 60]]

## God Nodes (most connected - your core abstractions)
1. `load()` - 139 edges
2. `save()` - 96 edges
3. `today()` - 58 edges
4. `compute_consistency()` - 30 edges
5. `catalog_maps()` - 28 edges
6. `build_project_detail_context()` - 28 edges
7. `parse_quote_csv()` - 27 edges
8. `parse_ldm_csv()` - 24 edges
9. `active_drive_paths()` - 24 edges
10. `missing_ldm_items_from_bundles()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `Catalog Hydration Logic` --semantically_similar_to--> `Consistency COT vs LDM Module`  [INFERRED] [semantically similar]
  logica_cuantificaciones.txt → VERSIONES.md
- `mobile_projects()` --calls--> `load()`  [INFERRED]
  tracker\routes\quotes_mobile.py → tracker\storage.py
- `Lista de Materiales (LDM) Data Structure` --implements--> `materials.py import_ldm_csv route`  [INFERRED]
  REFERENCIA_ESTRUCTURAS_CSV.txt → tracker/routes/materials.py
- `CSV→LDM Import Diff Algorithm` --rationale_for--> `csv_import.py parse_ldm_csv()`  [INFERRED]
  logica_cuantificaciones.txt → tracker/csv_import.py
- `CSV→LDM Import Diff Algorithm` --rationale_for--> `materials.py import_ldm_csv route`  [INFERRED]
  logica_cuantificaciones.txt → tracker/routes/materials.py

## Hyperedges (group relationships)
- **he_delete_pattern** — base_modal_del, base_confirm_js, fi_table, tm_cards, cat_impact, pv_table [EXTRACTED 1.00]
- **he_admin_crud** — fi_tpl, tm_tpl, cat_tpl, pv_tpl [INFERRED 0.95]
- **he_session_close** — ver_current, ver_changelog, rm_checklist [EXTRACTED 1.00]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (114): activate_bundle_version_route(), add_bundle_version_route(), add_comparison_ignored(), api_catalogo(), api_catalogo_add(), api_catalogo_categorias(), api_catalogo_impact(), bulk_delete_catalogo() (+106 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (98): approve_quote_route(), audit_deleted_catalog(), _build_quote_workbook(), delete_quote(), edit_quote(), _find_project(), _flash_csv_catalog_errors(), import_quote_csv() (+90 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (92): ldm_pdf(), create_drive_folder(), Crea la carpeta Drive del proyecto si aún no existe., Crea la carpeta Drive del proyecto si aún no existe., Crea la carpeta Drive del proyecto si aún no existe., quote_pdf(), DriveCsvStatusTest, active_drive_paths() (+84 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (74): LdmSyncTest, MaterialsSyncRouteTest, Pruebas de sincronizacion parcial LDM desde bundles., setUpClass(), activate_bundle_version(), add_bundle_version(), bundle_by_catalog_item_id(), _clean() (+66 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (36): _discipline_list(), _find_draft(), _find_project(), mobile_add_item(), mobile_generate_pdf(), mobile_items(), mobile_projects(), mobile_review() (+28 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (66): Inyeccion app_version via Context Processor, Status Badges CSS bs-* ps-* src-*, Bootstrap Icons 1.11.3 CDN, Bootstrap 5.3.2 CDN, JS confirmDelete y submitFormWithConfirm, Flash Messages Display, Base Layout Template base.html, Modal Confirmacion Destructiva #modalConfirmDelete (+58 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (50): api_ldm_set_costo(), _attach_csv_item_metadata(), _bundle_suggestion_ldm(), _bundle_sync_suggestions(), _clean_form_text(), _clear_pdf_import(), _csv_already_imported(), _csv_item_lookup() (+42 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (55): active_ignored_items(), _clean(), ignored_catalog_ids(), ignored_catalog_map(), normalize_ignored_item(), Artículos ignorados en comparación COT/LDM.  Los artículos ignorados siguen form, Normaliza una regla de artículo ignorado., Devuelve reglas activas aplicables al scope solicitado. (+47 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (26): LdmCsvImportTest, CSV escrito en cp1252 (fallback ANSI del LISP) debe retornar error         legib, CSV escrito en cp1252 (fallback ANSI del LISP) debe retornar error         legib, LdmTubeFixturesTest, Tests parametrizados para importación CSV de tubería conduit.  Cubre los 6 tipos, Múltiples tipos de tubería en un mismo archivo LDM., Metadata #proveedor y #fecha post-header (formato real del LISP)., Escribe un CSV LDM con header estándar y filas dadas.      meta_rows: lista de t (+18 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (25): QuoteCsvImportTest, QuoteSymbolFixturesTest, CSV escrito en cp1252 (fallback ANSI del LISP) debe retornar error         legib, CSV escrito en cp1252 (fallback ANSI del LISP) debe retornar error         legib, CSV escrito en cp1252 (fallback ANSI del LISP) debe retornar error         legib, CotTubeFixturesTest, Metadata #proyecto_clave y #quote_type del archivo COT LISP., Múltiples tipos y diámetros en un solo archivo COT. (+17 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (48): API Endpoint /api/catalogo/add, API Endpoint /api/catalogo/bulk-delete, API Endpoint /api/catalogo, Audit Deleted Catalog Template, Base Layout Template, Bundle Entity (COT Commercial Item + LDM Components), Bundles Template, Catalog Inline AJAX Edit Pattern (+40 more)

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (22): login(), new_user(), reset_password(), toggle_user(), users(), AdminRequiredTestCase, AuthTestCase, create_user() (+14 more)

### Community 12 - "Community 12"
Cohesion: 0.12
Nodes (32): ProjectViewTest, check_blocked(), currency(), fdate(), get_progress(), today_short(), _as_float(), build_consistency_view() (+24 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (16): AggregateLdmItemsTest, AggregateQuoteItemsTest, BundleConsistencyIntegrationTest, ClassifyMarginTest, CompareItemsTest, ComputeConsistencyTest, IgnoredItemsConsistencyTest, _l_item() (+8 more)

### Community 14 - "Community 14"
Cohesion: 0.07
Nodes (39): catalog.py hydrate_quote/ldm(), CLAUDE.md Graphify Rules, consistency.py compute_consistency(), csv_import.py parse_ldm_csv(), CSV Import API Routes (Pending), Catálogo Data Structure, Cotización al Cliente (COT) Data Structure, Lista de Materiales (LDM) Data Structure (+31 more)

### Community 15 - "Community 15"
Cohesion: 0.08
Nodes (8): MobileAddItemTest, MobileGeneratePdfTest, MobileItemsTest, MobileProjectsTest, MobileRemoveItemTest, MobileReviewTest, MobileRouteTestBase, Integration tests for the mobile quote blueprint (Fase 10).

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (8): ApiCatalogoTest, FilterCatalogTest, ListCategoriesTest, MatchItemTest, Pruebas para tracker.catalog_search y la API /api/catalogo., Smoke-test del endpoint JSON; no muta datos., setUpClass(), TokenizeTest

### Community 17 - "Community 17"
Cohesion: 0.08
Nodes (6): BundleEdgeCasesTest, BundleVersioningTest, ExpandQuoteBundlesTest, Casos borde de expand_quote_bundles y versionado., Cobertura de los bundles reales en data/bundles.json., SeededBundlesTest

### Community 18 - "Community 18"
Cohesion: 0.21
Nodes (12): ValidatorsTest, _clean(), _deleted_catalog_item_at(), _is_blank(), _parse_float(), _parse_ldm_items(), _parse_quote_items(), _validate_iso_date() (+4 more)

### Community 19 - "Community 19"
Cohesion: 0.22
Nodes (25): build_ldm_pdf(), build_progress_pdf(), build_quote_pdf(), _company_name(), format_date_long(), _load_company(), money_pdf(), note_lines() (+17 more)

### Community 20 - "Community 20"
Cohesion: 0.16
Nodes (15): AdminFilterHelpersTest, AdminFilterRouteTest, Pruebas de filtros administrativos para proveedores y fichas., setUpClass(), filter_fichas(), filter_proveedores(), _indexed(), list_field_values() (+7 more)

### Community 21 - "Community 21"
Cohesion: 0.19
Nodes (5): KanbanRouteTest, ProjectStageTest, _task(), project_stage(), Derive the portfolio stage from existing task data + the in_obra flag.      Stag

### Community 22 - "Community 22"
Cohesion: 0.17
Nodes (1): AvanceRoutesTest

### Community 23 - "Community 23"
Cohesion: 0.29
Nodes (13): filter_catalog(), _indexable_text(), list_categories(), match_item(), _normalize(), Búsqueda y filtrado del catálogo.  Funciones puras (sin I/O) para reutilizar ent, Quita acentos y baja a minúsculas para comparar texto en español., Divide la query en tokens normalizados, descartando vacíos. (+5 more)

### Community 24 - "Community 24"
Cohesion: 0.23
Nodes (6): CsvCatalogValidationTest, _catalog_index(), _clean(), Validate parsed CSV rows against catalog name and unit.      Matching intentiona, _unit_key(), validate_csv_catalog_items()

### Community 25 - "Community 25"
Cohesion: 0.23
Nodes (3): SemaphoreTest, project_semaphore(), Returns 'verde', 'amarillo', 'rojo', or 'gris' based on deadline and inactivity.

### Community 26 - "Community 26"
Cohesion: 0.33
Nodes (13): _clean(), _extract_from_tables(), _extract_from_text(), extract_items_from_pdf(), _extract_procables(), _extract_procables_meta(), _header_map(), _is_procables() (+5 more)

### Community 27 - "Community 27"
Cohesion: 0.15
Nodes (2): CsvCotFilenameTest, Tests para parse_csv_cot_filename y decorate_csv_cot.

### Community 28 - "Community 28"
Cohesion: 0.23
Nodes (3): AdminBundlesRoutesTest, Smoke tests de UI Admin para bundles., setUpClass()

### Community 29 - "Community 29"
Cohesion: 0.27
Nodes (1): AdminFormsTest

### Community 30 - "Community 30"
Cohesion: 0.27
Nodes (5): empresa(), empresa_logo(), CompanyConfigTest, get_company(), save_company()

### Community 31 - "Community 31"
Cohesion: 0.22
Nodes (2): ProjectDetailBundleUITest, Smoke tests for simplified project detail COT/LDM UI.

### Community 32 - "Community 32"
Cohesion: 0.29
Nodes (2): QuoteCsvImportRouteTest, setUpClass()

### Community 33 - "Community 33"
Cohesion: 0.39
Nodes (3): MaterialsCsvExportTest, Tests for exporting an existing LDM as CSV., setUpClass()

### Community 34 - "Community 34"
Cohesion: 0.48
Nodes (3): AuditDeletedCatalogRouteTest, Tests for the deleted catalog audit route., setUpClass()

### Community 35 - "Community 35"
Cohesion: 0.33
Nodes (2): LdmPdfImportRoutesTest, setUpClass()

### Community 36 - "Community 36"
Cohesion: 0.29
Nodes (1): ConversionRulesTest

### Community 37 - "Community 37"
Cohesion: 0.33
Nodes (1): ComparisonIgnoredTest

### Community 38 - "Community 38"
Cohesion: 0.4
Nodes (1): LdmCsvImportRouteTest

### Community 39 - "Community 39"
Cohesion: 0.7
Nodes (3): iter_python_files(), main(), Parse project Python files without writing bytecode.

### Community 40 - "Community 40"
Cohesion: 0.5
Nodes (2): _is_truthy(), Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.

### Community 41 - "Community 41"
Cohesion: 0.67
Nodes (3): Flask Dependency, openpyxl Dependency, Tech Stack Declaration

### Community 42 - "Community 42"
Cohesion: 0.67
Nodes (1): fpdf2 Dependency

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (2): Data Integrity Rules (R1-R7), ProjectTracker System Rationale

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Roadmap Completed Features

## Knowledge Gaps
- **285 isolated node(s):** `Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.`, `Cobertura de los bundles reales en data/bundles.json.`, `Casos borde de expand_quote_bundles y versionado.`, `Smoke-test del endpoint JSON; no muta datos.`, `Sin General, usa la Preliminar más reciente. Las Extraordinarias no son base.` (+280 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 22`** (19 nodes): `AvanceRoutesTest`, `._get_project()`, `.tearDown()`, `.test_add_doc_checklist_appends_item()`, `.test_add_doc_checklist_ignores_empty_name()`, `.test_add_multiple_docs_independent()`, `.test_delete_doc_checklist_removes_item()`, `.test_progress_pdf_returns_pdf_content()`, `.test_progress_pdf_unknown_project_404()`, `.test_toggle_doc_checklist_flips_done()`, `.test_update_stage_budget_handles_missing_values_as_zero()`, `.test_update_stage_budget_persists_values()`, `.test_update_stage_budget_skips_without_template()`, `.test_update_stage_budget_unknown_project_redirects()`, `.test_update_stage_status_empty_date_stored_as_none()`, `.test_update_stage_status_ignores_empty_stage()`, `.test_update_stage_status_sets_stage()`, `.test_update_stage_status_unknown_project_redirects()`, `test_avance_routes.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (13 nodes): `test_drive.py`, `CsvCotFilenameTest`, `.setUp()`, `.test_case_insensitive()`, `.test_decorate_marks_desactualizado_when_newer_exists()`, `.test_decorate_marks_importado_when_linked()`, `.test_decorate_marks_pending_unlinked()`, `.test_parses_valid_cot_csv()`, `.test_rejects_ldm_csv()`, `.test_rejects_wrong_clave()`, `.test_version_key_invalid_returns_sentinel()`, `.test_version_key_ordering()`, `Tests para parse_csv_cot_filename y decorate_csv_cot.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (11 nodes): `test_admin_forms.py`, `AdminFormsTest`, `.assert_invalid_form_preserved()`, `.setUp()`, `.test_catalogo_invalid_form_preserves_capture()`, `.test_fichas_invalid_form_preserves_capture()`, `.test_proveedores_invalid_form_preserves_capture()`, `.test_settings_invalid_path_preserves_capture()`, `.test_team_invalid_form_preserves_capture()`, `test_admin_forms.py`, `test_admin_forms.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (11 nodes): `test_project_detail_bundle_ui.py`, `ProjectDetailBundleUITest`, `.test_materials_tab_exposes_assisted_bundle_sync_review()`, `.test_materials_tab_exposes_csv_export_for_existing_ldms()`, `.test_materials_tab_exposes_partial_bundle_sync()`, `.test_materials_tab_hides_partial_bundle_sync()`, `.test_template_contains_bundle_technical_consistency_section()`, `.test_template_contains_simple_cot_ldm_summary()`, `test_project_detail_bundle_ui.py`, `Smoke tests for simplified project detail COT/LDM UI.`, `test_project_detail_bundle_ui.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (8 nodes): `test_quote_csv_import_route.py`, `QuoteCsvImportRouteTest`, `._fake_load()`, `.test_import_quote_csv_blocks_unit_mismatch()`, `.test_import_quote_csv_drive_blocks_catalog_validation()`, `.test_import_quote_csv_renders_editable_preview()`, `setUpClass()`, `test_quote_csv_import_route.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (7 nodes): `test_ldm_pdf_import_routes.py`, `LdmPdfImportRoutesTest`, `.test_create_pdf_import_is_blocked_when_project_is_closed()`, `.test_upload_pdf_is_blocked_when_project_is_closed()`, `.test_upload_stores_pdf_import_payload_outside_cookie_session()`, `test_ldm_pdf_import_routes.py`, `setUpClass()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (7 nodes): `ConversionRulesTest`, `.test_aggregate_ldm_converts_to_expected_id()`, `.test_compare_expected_vs_actual_marks_shortage_and_excess()`, `.test_ldm_piece_to_cot_linear_meter()`, `.test_tolerance_accepts_small_differences()`, `test_comparison_rules.py`, `test_comparison_rules.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (6 nodes): `ComparisonIgnoredTest`, `.test_filters_by_scope_and_active()`, `.test_split_ignored_linked()`, `.test_summarize_ignored()`, `test_comparison_ignored.py`, `test_comparison_ignored.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (5 nodes): `LdmCsvImportRouteTest`, `._fake_load()`, `.test_import_ldm_csv_blocks_missing_catalog_before_preview()`, `test_ldm_csv_import_route.py`, `setUpClass()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (4 nodes): `app.py`, `app.py`, `_is_truthy()`, `Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (3 nodes): `pdfs.py build_ldm_pdf()`, `pdfs.py build_quote_pdf()`, `fpdf2 Dependency`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (2 nodes): `Data Integrity Rules (R1-R7)`, `ProjectTracker System Rationale`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `Roadmap Completed Features`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load()` connect `Community 0` to `Community 1`, `Community 2`, `Community 4`, `Community 6`, `Community 12`, `Community 22`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `parse_quote_csv()` connect `Community 9` to `Community 1`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `import_ldm_csv()` connect `Community 6` to `Community 0`, `Community 8`, `Community 18`, `Community 24`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 136 inferred relationships involving `load()` (e.g. with `.setUp()` and `._get_project()`) actually correct?**
  _`load()` has 136 INFERRED edges - model-reasoned connections that need verification._
- **Are the 93 inferred relationships involving `save()` (e.g. with `.setUp()` and `.tearDown()`) actually correct?**
  _`save()` has 93 INFERRED edges - model-reasoned connections that need verification._
- **Are the 55 inferred relationships involving `today()` (e.g. with `next_quote_number()` and `delete_catalog_items_data()`) actually correct?**
  _`today()` has 55 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `compute_consistency()` (e.g. with `quote_type_key()` and `build_project_detail_context()`) actually correct?**
  _`compute_consistency()` has 10 INFERRED edges - model-reasoned connections that need verification._