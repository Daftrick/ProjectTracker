# Community 0

> 132 nodes · cohesion 0.04

## Key Concepts

- [load()](file:///Users/macbook/ProjectTracker/tracker/storage.py#L37) (111 connections)
- [save()](file:///Users/macbook/ProjectTracker/tracker/storage.py#L46) (74 connections)
- [admin.py](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py#L1) (67 connections)
- [today()](file:///Users/macbook/ProjectTracker/tracker/storage.py#L63) (53 connections)
- [projects.py](file:///Users/macbook/ProjectTracker/tracker/routes/projects.py#L1) (26 connections)
- [storage.py](file:///Users/macbook/ProjectTracker/tracker/storage.py#L1) (22 connections)
- [new_id()](file:///Users/macbook/ProjectTracker/tracker/storage.py#L59) (15 connections)
- [quotes_mobile.py](file:///Users/macbook/ProjectTracker/tracker/routes/quotes_mobile.py#L1) (14 connections)
- [deletions.py](file:///Users/macbook/ProjectTracker/tracker/deletions.py#L1) (12 connections)
- [add_bundle_version_route()](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py#L527) (11 connections)
- [bundles()](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py#L442) (10 connections)
- [new_ldm()](file:///Users/macbook/ProjectTracker/tracker/routes/materials.py#L219) (10 connections)
- [catalogo()](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py#L175) (9 connections)
- [update_bundle_version()](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py#L505) (9 connections)
- [mobile_generate_pdf()](file:///Users/macbook/ProjectTracker/tracker/routes/quotes_mobile.py#L159) (9 connections)
- [fichas()](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py#L647) (8 connections)
- [proveedores()](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py#L584) (8 connections)
- [team()](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py#L722) (8 connections)
- [create_app()](file:///Users/macbook/ProjectTracker/tracker/__init__.py#L47) (8 connections)
- [_bundle_suggestion_ldm()](file:///Users/macbook/ProjectTracker/tracker/routes/materials.py#L157) (8 connections)
- [get_project_templates()](file:///Users/macbook/ProjectTracker/tracker/templates_config.py#L17) (8 connections)
- [update_bundle()](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py#L472) (7 connections)
- [new_project()](file:///Users/macbook/ProjectTracker/tracker/routes/projects.py#L70) (7 connections)
- [mobile_items()](file:///Users/macbook/ProjectTracker/tracker/routes/quotes_mobile.py#L62) (7 connections)
- [activate_bundle_version_route()](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py#L552) (6 connections)
- *... and 107 more nodes in this community*

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
```

## Relationships

- No strong cross-community connections detected

## Source Files

- [/Users/macbook/ProjectTracker/tests/test_avance_routes.py](file:///Users/macbook/ProjectTracker/tests/test_avance_routes.py)
- [/Users/macbook/ProjectTracker/tests/test_company_templates.py](file:///Users/macbook/ProjectTracker/tests/test_company_templates.py)
- [/Users/macbook/ProjectTracker/tracker/__init__.py](file:///Users/macbook/ProjectTracker/tracker/__init__.py)
- [/Users/macbook/ProjectTracker/tracker/catalog.py](file:///Users/macbook/ProjectTracker/tracker/catalog.py)
- [/Users/macbook/ProjectTracker/tracker/deletions.py](file:///Users/macbook/ProjectTracker/tracker/deletions.py)
- [/Users/macbook/ProjectTracker/tracker/domain.py](file:///Users/macbook/ProjectTracker/tracker/domain.py)
- [/Users/macbook/ProjectTracker/tracker/routes/admin.py](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py)
- [/Users/macbook/ProjectTracker/tracker/routes/materials.py](file:///Users/macbook/ProjectTracker/tracker/routes/materials.py)
- [/Users/macbook/ProjectTracker/tracker/routes/projects.py](file:///Users/macbook/ProjectTracker/tracker/routes/projects.py)
- [/Users/macbook/ProjectTracker/tracker/routes/quotes.py](file:///Users/macbook/ProjectTracker/tracker/routes/quotes.py)
- [/Users/macbook/ProjectTracker/tracker/routes/quotes_mobile.py](file:///Users/macbook/ProjectTracker/tracker/routes/quotes_mobile.py)
- [/Users/macbook/ProjectTracker/tracker/services.py](file:///Users/macbook/ProjectTracker/tracker/services.py)
- [/Users/macbook/ProjectTracker/tracker/storage.py](file:///Users/macbook/ProjectTracker/tracker/storage.py)
- [/Users/macbook/ProjectTracker/tracker/templates_config.py](file:///Users/macbook/ProjectTracker/tracker/templates_config.py)

## Audit Trail

- EXTRACTED: 394 (44%)
- INFERRED: 508 (56%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*