# Community 0

> 182 nodes · cohesion 0.03

## Key Concepts

- [load()](file:///Users/macbook/Documents/ProjectTracker/tracker/storage.py#L40) (151 connections)
- [save()](file:///Users/macbook/Documents/ProjectTracker/tracker/storage.py#L49) (112 connections)
- [admin.py](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/admin.py#L1) (66 connections)
- [today()](file:///Users/macbook/Documents/ProjectTracker/tracker/storage.py#L66) (57 connections)
- [projects.py](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/projects.py#L1) (29 connections)
- [storage.py](file:///Users/macbook/Documents/ProjectTracker/tracker/storage.py#L1) (25 connections)
- [create_app()](file:///Users/macbook/Documents/ProjectTracker/tracker/__init__.py#L53) (21 connections)
- [new_id()](file:///Users/macbook/Documents/ProjectTracker/tracker/storage.py#L62) (20 connections)
- [domain.py](file:///Users/macbook/Documents/ProjectTracker/tracker/domain.py#L1) (20 connections)
- [__init__.py](file:///Users/macbook/Documents/ProjectTracker/tracker/__init__.py#L1) (18 connections)
- [import_ldm_csv_upload()](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/materials.py#L267) (15 connections)
- [deletions.py](file:///Users/macbook/Documents/ProjectTracker/tracker/deletions.py#L1) (12 connections)
- [add_bundle_version_route()](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/admin.py#L513) (11 connections)
- [import_ldm_pdf_create()](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/materials.py#L778) (11 connections)
- [form_models.py](file:///Users/macbook/Documents/ProjectTracker/tracker/form_models.py#L1) (11 connections)
- [bundles()](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/admin.py#L428) (10 connections)
- [new_ldm()](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/materials.py#L219) (10 connections)
- [update_bundle_version()](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/admin.py#L491) (9 connections)
- [QuoteClientOverrideRoutesTest](file:///Users/macbook/Documents/ProjectTracker/tests/test_quote_client_override.py#L95) (9 connections)
- [catalogo()](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/admin.py#L165) (8 connections)
- [_bundle_suggestion_ldm()](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/materials.py#L157) (8 connections)
- [get_project_templates()](file:///Users/macbook/Documents/ProjectTracker/tracker/templates_config.py#L17) (8 connections)
- [ProyectoEjecutivoQuoteRoutesTest](file:///Users/macbook/Documents/ProjectTracker/tests/test_proyecto_ejecutivo_quote.py#L26) (8 connections)
- [QuoteDescTextareaRouteTest](file:///Users/macbook/Documents/ProjectTracker/tests/test_quote_desc_textarea.py#L64) (8 connections)
- [fichas()](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/admin.py#L628) (7 connections)
- *... and 157 more nodes in this community*

## Class Diagram

```mermaid
classDiagram
    class ProjectTemplatesTest {
        +test_company_templates.py()
        +.test_returns_defaults_when_no_file()
        +.test_returns_defaults_when_empty_list()
        +.test_returns_stored_templates()
        +.test_default_templates_have_stages_list()
        +.test_save_templates_calls_storage()
    }
    class FinancialCardRouteTest {
        +test_project_financial_card_payments.py()
        +.setUp()
        +.tearDown()
        +.test_project_detail_page_shows_paid_amount_and_balance()
        +.test_project_detail_page_shows_zero_paid_without_payments()
    }
    class ProyectoEjecutivoQuoteRoutesTest {
        +test_proyecto_ejecutivo_quote.py()
        +.setUp()
        +.tearDown()
        +._quote_form()
        +.test_new_quote_form_offers_proyecto_ejecutivo_option()
        +.test_creates_quote_with_j_sequence_and_qty_one()
        +.test_view_page_hides_unidad_and_cantidad_columns()
        +.test_second_quote_increments_j_sequence()
    }
    class QuoteClientOverrideRoutesTest {
        +test_quote_client_override.py()
        +.setUp()
        +.tearDown()
        +._base_quote_form()
        +.test_new_quote_with_client_unchanged_has_no_override()
        +.test_new_quote_with_edited_client_saves_override()
        +.test_override_survives_later_project_client_change()
        +.test_edit_quote_updates_proposal_for()
        +.test_new_quote_form_prefills_client_with_project_client()
    }
    class QuoteClientSyncRoutesTest {
        +test_quote_client_sync.py()
        +.setUp()
        +.tearDown()
        +.test_quote_detail_page_shows_current_client()
        +.test_quote_resumen_page_shows_current_client()
    }
    class QuoteDescTextareaRouteTest {
        +test_quote_desc_textarea.py()
        +.setUp()
        +.tearDown()
        +.test_edit_form_renders_textarea_with_content()
        +.test_new_quote_form_renders_empty_textarea()
        +.test_description_with_special_chars_is_escaped_as_text_content()
        +.test_multiline_description_round_trips_through_save()
        +.test_quote_view_page_preserves_line_breaks_visually()
    }
    class QuotePaymentsLinkRouteTest {
        +test_quote_payments_link.py()
        +.setUp()
        +.tearDown()
        +.test_project_detail_page_renders_payments_button_for_quote_row()
        +.test_view_quote_page_has_payments_anchor()
        +.test_payments_button_visible_even_for_closed_project()
    }
```

## Relationships

- [[Community 1]] (2 shared connections)
- [[Community 17]] (1 shared connections)
- [[Community 2]] (1 shared connections)

## Source Files

- [/Users/macbook/Documents/ProjectTracker/tests/test_avance_routes.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_avance_routes.py)
- [/Users/macbook/Documents/ProjectTracker/tests/test_company_templates.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_company_templates.py)
- [/Users/macbook/Documents/ProjectTracker/tests/test_deletions.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_deletions.py)
- [/Users/macbook/Documents/ProjectTracker/tests/test_project_financial_card_payments.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_project_financial_card_payments.py)
- [/Users/macbook/Documents/ProjectTracker/tests/test_proyecto_ejecutivo_quote.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_proyecto_ejecutivo_quote.py)
- [/Users/macbook/Documents/ProjectTracker/tests/test_quote_client_override.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_quote_client_override.py)
- [/Users/macbook/Documents/ProjectTracker/tests/test_quote_client_sync.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_quote_client_sync.py)
- [/Users/macbook/Documents/ProjectTracker/tests/test_quote_desc_textarea.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_quote_desc_textarea.py)
- [/Users/macbook/Documents/ProjectTracker/tests/test_quote_payments_link.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_quote_payments_link.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/__init__.py](file:///Users/macbook/Documents/ProjectTracker/tracker/__init__.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/catalog.py](file:///Users/macbook/Documents/ProjectTracker/tracker/catalog.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/deletions.py](file:///Users/macbook/Documents/ProjectTracker/tracker/deletions.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/domain.py](file:///Users/macbook/Documents/ProjectTracker/tracker/domain.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/form_models.py](file:///Users/macbook/Documents/ProjectTracker/tracker/form_models.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/routes/admin.py](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/admin.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/routes/materials.py](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/materials.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/routes/projects.py](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/projects.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/routes/quotes.py](file:///Users/macbook/Documents/ProjectTracker/tracker/routes/quotes.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/storage.py](file:///Users/macbook/Documents/ProjectTracker/tracker/storage.py)
- [/Users/macbook/Documents/ProjectTracker/tracker/templates_config.py](file:///Users/macbook/Documents/ProjectTracker/tracker/templates_config.py)

## Audit Trail

- EXTRACTED: 530 (45%)
- INFERRED: 654 (55%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*