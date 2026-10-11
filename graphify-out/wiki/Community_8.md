# Community 8

> 68 nodes · cohesion 0.05

## Key Concepts

- [parse_ldm_csv()](file:///Users/macbook/ProjectTracker/tracker/csv_import.py#L79) (21 connections)
- [LdmTubeFixturesTest](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py#L139) (17 connections)
- [CotTubeFixturesTest](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py#L282) (16 connections)
- [._run_ldm_case()](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py#L141) (16 connections)
- [._run_cot_case()](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py#L284) (14 connections)
- [csv_import.py](file:///Users/macbook/ProjectTracker/tracker/csv_import.py#L1) (11 connections)
- [LdmCsvImportTest](file:///Users/macbook/Documents/ProjectTracker/tests/test_csv_import.py#L8) (9 connections)
- [_write_cot()](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py#L67) (6 connections)
- [_clean()](file:///Users/macbook/ProjectTracker/tracker/csv_import.py#L11) (5 connections)
- [_write_ldm()](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py#L52) (5 connections)
- [test_tube_fixtures.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py#L1) (5 connections)
- [_build_catalog_index()](file:///Users/macbook/ProjectTracker/tracker/csv_import.py#L64) (4 connections)
- [_first_value()](file:///Users/macbook/ProjectTracker/tracker/csv_import.py#L19) (4 connections)
- [_header_key()](file:///Users/macbook/ProjectTracker/tracker/csv_import.py#L15) (4 connections)
- [_match_catalog()](file:///Users/macbook/ProjectTracker/tracker/csv_import.py#L74) (4 connections)
- [_parse_float()](file:///Users/macbook/ProjectTracker/tracker/csv_import.py#L26) (4 connections)
- [.test_cot_mixed_tubes_single_file()](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py#L353) (4 connections)
- [.test_cot_total_rounding_two_decimals()](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py#L373) (4 connections)
- [.test_cot_with_metadata_proyecto_clave_and_quote_type()](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py#L337) (4 connections)
- [.test_ldm_mixed_tubes_single_file()](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py#L195) (4 connections)
- [.test_ldm_with_metadata_proveedor_fecha()](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py#L213) (4 connections)
- [_detect_dialect()](file:///Users/macbook/ProjectTracker/tracker/csv_import.py#L54) (3 connections)
- [.test_parse_ldm_csv_returns_error_on_ansi_encoding()](file:///Users/macbook/Documents/ProjectTracker/tests/test_csv_import.py#L111) (3 connections)
- [_read_sample()](file:///Users/macbook/ProjectTracker/tracker/csv_import.py#L46) (2 connections)
- [.test_parse_ldm_csv_accepts_spanish_headers_and_semicolon()](file:///Users/macbook/Documents/ProjectTracker/tests/test_csv_import.py#L30) (2 connections)
- *... and 43 more nodes in this community*

## Class Diagram

```mermaid
classDiagram
    class LdmCsvImportTest {
        +test_csv_import.py()
        +.test_parse_ldm_csv_reads_items_and_metadata()
        +.test_parse_ldm_csv_accepts_spanish_headers_and_semicolon()
        +.test_parse_ldm_csv_reports_missing_required_headers()
        +.test_parse_ldm_csv_auto_links_catalog_item_id()
        +.test_parse_ldm_csv_catalog_match_is_case_insensitive()
        +.test_parse_ldm_csv_catalog_match_uses_catalog_name_key()
        +.test_parse_ldm_csv_without_catalog_sets_empty_catalog_item_id()
        +.test_parse_ldm_csv_returns_error_on_ansi_encoding()
    }
    class CotTubeFixturesTest {
        +test_tube_fixtures.py()
        +._run_cot_case()
        +.test_cot_galvanizado_pared_delgada_27mm_sin_precio()
        +.test_cot_galvanizado_pared_delgada_63mm_con_precio()
        +.test_cot_galvanizado_pared_gruesa_27mm_sin_precio()
        +.test_cot_galvanizado_pared_gruesa_63mm_con_precio()
        +.test_cot_pvc_sp_27mm_con_precio()
        +.test_cot_pvc_sp_63mm_sin_precio()
        +.test_cot_pad_flexible_corrugado_63mm_con_precio()
        +.test_cot_metalico_flexible_35mm_con_precio()
    }
    class LdmTubeFixturesTest {
        +test_tube_fixtures.py()
        +._run_ldm_case()
        +.test_ldm_galvanizado_pared_delgada_27mm()
        +.test_ldm_galvanizado_pared_delgada_41mm()
        +.test_ldm_galvanizado_pared_delgada_63mm()
        +.test_ldm_galvanizado_pared_gruesa_27mm()
        +.test_ldm_galvanizado_pared_gruesa_63mm()
        +.test_ldm_pvc_sp_27mm()
        +.test_ldm_pvc_sp_63mm()
        +.test_ldm_pad_flexible_corrugado_35mm()
    }
```

## Relationships

- [[Community 10]] (7 shared connections)
- [[Community 21]] (5 shared connections)

## Source Files

- [/Users/macbook/Documents/ProjectTracker/tests/test_csv_import.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_csv_import.py)
- [/Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_tube_fixtures.py)
- [/Users/macbook/ProjectTracker/tests/test_csv_import.py](file:///Users/macbook/ProjectTracker/tests/test_csv_import.py)
- [/Users/macbook/ProjectTracker/tests/test_tube_fixtures.py](file:///Users/macbook/ProjectTracker/tests/test_tube_fixtures.py)
- [/Users/macbook/ProjectTracker/tracker/csv_import.py](file:///Users/macbook/ProjectTracker/tracker/csv_import.py)

## Audit Trail

- EXTRACTED: 218 (88%)
- INFERRED: 30 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*