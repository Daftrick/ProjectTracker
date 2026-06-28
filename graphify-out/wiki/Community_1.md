# Community 1

> 90 nodes · cohesion 0.04

## Key Concepts

- [auth.py](file:///Users/macbook/ProjectTracker/tracker/auth.py#L1) (30 connections)
- [__init__.py](file:///Users/macbook/ProjectTracker/tracker/__init__.py#L1) (18 connections)
- [auth_routes.py](file:///Users/macbook/ProjectTracker/tracker/routes/auth_routes.py#L1) (16 connections)
- [AuthTestCase](file:///Users/macbook/ProjectTracker/tests/test_auth.py#L7) (12 connections)
- [_db_execute()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L154) (9 connections)
- [init_db()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L25) (9 connections)
- [AdminRequiredTestCase](file:///Users/macbook/ProjectTracker/tests/test_auth.py#L107) (8 connections)
- [DefaultAdminTests](file:///Users/macbook/ProjectTracker/tests/test_auth_defaults.py#L12) (8 connections)
- [CompanyLogoUploadTests](file:///Users/macbook/ProjectTracker/tests/test_company_logo_upload.py#L8) (7 connections)
- [verify_credentials()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L175) (6 connections)
- [_requires_configured_secret_key()](file:///Users/macbook/ProjectTracker/tracker/__init__.py#L43) (6 connections)
- [._create_user()](file:///Users/macbook/ProjectTracker/tests/test_auth.py#L35) (6 connections)
- [create_user()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L190) (5 connections)
- [User](file:///Users/macbook/ProjectTracker/tracker/auth.py#L101) (5 connections)
- [AppConfigTests](file:///Users/macbook/ProjectTracker/tests/test_app_config.py#L8) (5 connections)
- [._login_as()](file:///Users/macbook/ProjectTracker/tests/test_auth.py#L133) (5 connections)
- [_db_query()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L148) (4 connections)
- [get_user_by_username()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L167) (4 connections)
- [reset_user_password()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L201) (4 connections)
- [set_user_active()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L197) (4 connections)
- [.test_inactive_user_cannot_login()](file:///Users/macbook/ProjectTracker/tests/test_auth.py#L82) (4 connections)
- [._admin_row()](file:///Users/macbook/ProjectTracker/tests/test_auth_defaults.py#L29) (4 connections)
- [_default_admin_config()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L56) (3 connections)
- [delete_user()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L226) (3 connections)
- [_ensure_default_admin()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L63) (3 connections)
- *... and 65 more nodes in this community*

## Class Diagram

```mermaid
classDiagram
    class User {
        +auth.py()
        +.__init__()
    }
    class AppConfigTests {
        +test_app_config.py()
        +.test_default_secret_is_allowed_for_local_startup()
        +.test_default_secret_is_rejected_in_production()
        +.test_custom_secret_is_allowed_in_production()
    }
    class AdminRequiredTestCase {
        +test_auth.py()
        +.setUp()
        +.tearDown()
        +._login_as()
        +.test_cotizador_cannot_access_empresa()
        +.test_cotizador_cannot_access_users()
        +.test_admin_can_access_empresa()
        +.test_admin_can_access_users()
    }
    class AuthTestCase {
        +test_auth.py()
        +.setUp()
        +.tearDown()
        +._create_user()
        +._login()
        +.test_login_page_returns_200()
        +.test_unauthenticated_redirect_to_login()
        +.test_login_success_redirects_to_dashboard()
        +.test_login_wrong_password_shows_error()
        +.test_login_unknown_user_same_error()
    }
    class DefaultAdminTests {
        +test_auth_defaults.py()
        +.setUp()
        +.tearDown()
        +._admin_row()
        +.test_configured_default_admin_credentials_are_used_on_first_init()
        +.test_configured_password_does_not_reset_existing_admin_by_default()
        +.test_configured_password_can_reset_existing_admin_when_enabled()
    }
    class CompanyLogoUploadTests {
        +test_company_logo_upload.py()
        +.setUp()
        +.test_upload_accepts_real_png_and_saves_company_logo()
        +.test_empresa_preview_uses_serve_route_with_logo_version()
        +.test_upload_rejects_svg()
        +.test_upload_rejects_extension_that_does_not_match_content()
    }
```

## Relationships

- No strong cross-community connections detected

## Source Files

- [/Users/macbook/ProjectTracker/tests/test_app_config.py](file:///Users/macbook/ProjectTracker/tests/test_app_config.py)
- [/Users/macbook/ProjectTracker/tests/test_auth.py](file:///Users/macbook/ProjectTracker/tests/test_auth.py)
- [/Users/macbook/ProjectTracker/tests/test_auth_defaults.py](file:///Users/macbook/ProjectTracker/tests/test_auth_defaults.py)
- [/Users/macbook/ProjectTracker/tests/test_company_logo_upload.py](file:///Users/macbook/ProjectTracker/tests/test_company_logo_upload.py)
- [/Users/macbook/ProjectTracker/tracker/__init__.py](file:///Users/macbook/ProjectTracker/tracker/__init__.py)
- [/Users/macbook/ProjectTracker/tracker/auth.py](file:///Users/macbook/ProjectTracker/tracker/auth.py)
- [/Users/macbook/ProjectTracker/tracker/extensions.py](file:///Users/macbook/ProjectTracker/tracker/extensions.py)
- [/Users/macbook/ProjectTracker/tracker/routes/admin.py](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py)
- [/Users/macbook/ProjectTracker/tracker/routes/auth_routes.py](file:///Users/macbook/ProjectTracker/tracker/routes/auth_routes.py)

## Audit Trail

- EXTRACTED: 259 (83%)
- INFERRED: 54 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*