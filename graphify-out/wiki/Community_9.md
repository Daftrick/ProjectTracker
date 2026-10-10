# Community 9

> 66 nodes · cohesion 0.06

## Key Concepts

- [build_quote_pdf()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L243) (33 connections)
- [pdfs.py](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L1) (26 connections)
- [build_ldm_pdf()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L1388) (13 connections)
- [quote_cover_copy()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L200) (12 connections)
- [_safe_text()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L52) (10 connections)
- [build_progress_pdf()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L1874) (9 connections)
- [quote_sequence_from_number()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L195) (9 connections)
- [quote_project_basis_note()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L220) (8 connections)
- [QuoteCoverCopyTest](file:///Users/macbook/Documents/ProjectTracker/tests/test_pdfs.py#L13) (8 connections)
- [QuotePdfSectionsTest](file:///Users/macbook/Documents/ProjectTracker/tests/test_pdfs.py#L147) (8 connections)
- [QuoteSequenceFromNumberTest](file:///Users/macbook/Documents/ProjectTracker/tests/test_pdfs.py#L77) (8 connections)
- [_load_company()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L128) (7 connections)
- [QuoteProjectBasisNoteTest](file:///Users/macbook/Documents/ProjectTracker/tests/test_pdfs.py#L52) (6 connections)
- [test_pdfs.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_pdfs.py#L1) (6 connections)
- [catalog_description_lookup()](file:///Users/macbook/Documents/ProjectTracker/tracker/catalog.py#L182) (5 connections)
- [quote_logo_path()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L142) (5 connections)
- [_register_dejavu()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L71) (5 connections)
- [format_date_long()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L86) (4 connections)
- [format_date_short()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L100) (4 connections)
- [_hex_to_rgb()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L41) (4 connections)
- [money_pdf()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L112) (4 connections)
- [note_lines()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L121) (4 connections)
- [quote_catalog_description()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L236) (4 connections)
- [_company_name()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L165) (3 connections)
- [quote_scope_paragraphs()](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py#L169) (3 connections)
- *... and 41 more nodes in this community*

## Class Diagram

```mermaid
classDiagram
    class BundleBreakdownPdfRenderTest {
        +test_pdfs.py()
        +.test_pdf_with_bundle_item_renders_without_error()
    }
    class ProyectoEjecutivoPdfTest {
        +test_pdfs.py()
        +.test_no_unit_or_qty_columns_rendered()
    }
    class QuoteCoverCopyTest {
        +test_pdfs.py()
        +.test_proyecto()
        +.test_obra()
        +.test_servicio()
        +.test_extraordinaria_with_sequence()
        +.test_extraordinaria_no_sequence()
        +.test_preliminar()
        +.test_general_fallback()
    }
    class QuotePdfSectionsTest {
        +test_pdfs.py()
        +.test_bundle_breakdown_renders_quantities_without_component_prices()
        +.test_specs_terms_and_notes_render_as_independent_sections()
        +.test_discount_renders_before_tax_in_both_totals_boxes()
        +.test_no_discount_omits_discount_row()
        +.test_pdf_reflects_project_client_over_stale_quote_snapshot()
        +.test_pdf_falls_back_to_quote_client_snapshot_when_project_has_none()
        +.test_long_description_does_not_orphan_words_after_wrap()
    }
    class QuoteProjectBasisNoteTest {
        +test_pdfs.py()
        +.test_proyecto_with_source()
        +.test_proyecto_without_source()
        +.test_obra_returns_empty()
        +.test_servicio_returns_empty()
        +.test_extraordinaria_uses_note_field()
    }
    class QuoteSequenceFromNumberTest {
        +test_pdfs.py()
        +.test_proyecto_code()
        +.test_obra_code()
        +.test_servicio_code()
        +.test_extraordinaria_code()
        +.test_general_code()
        +.test_no_match()
        +.test_empty()
    }
```

## Relationships

- [[Community 2]] (6 shared connections)

## Source Files

- [/Users/macbook/Documents/ProjectTracker/tests/test_pdfs.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_pdfs.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/catalog.py](file:///Users/macbook/Documents/ProjectTracker/tracker/catalog.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/pdfs.py](file:///Users/macbook/Documents/ProjectTracker/tracker/pdfs.py)
- [/Users/macbook/ProjectTracker/tests/test_pdfs.py](file:///Users/macbook/ProjectTracker/tests/test_pdfs.py)

## Audit Trail

- EXTRACTED: 203 (71%)
- INFERRED: 81 (29%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*