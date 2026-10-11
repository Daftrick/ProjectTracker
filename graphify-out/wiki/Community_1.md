# Community 1

> 101 nodes · cohesion 0.04

## Key Concepts

- [auth.py](file:///Users/macbook/ProjectTracker/tracker/auth.py#L1) (30 connections)
- [.grant()](file:///Users/macbook/ProjectTracker/tests/test_priority_bugs.py#L74) (18 connections)
- [RemainingBugTests](file:///Users/macbook/ProjectTracker/tests/test_remaining_bugs.py#L16) (17 connections)
- [auth_routes.py](file:///Users/macbook/ProjectTracker/tracker/routes/auth_routes.py#L1) (16 connections)
- [.snapshot()](file:///Users/macbook/ProjectTracker/tests/test_priority_bugs.py#L77) (13 connections)
- [AuthTestCase](file:///Users/macbook/ProjectTracker/tests/test_auth.py#L7) (12 connections)
- [IsolatedPriorityTests](file:///Users/macbook/ProjectTracker/tests/test_priority_bugs.py#L81) (12 connections)
- [init_db()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L25) (11 connections)
- [.close()](file:///Users/macbook/ProjectTracker/tests/test_remaining_bugs.py#L50) (10 connections)
- [_db_execute()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L154) (9 connections)
- [verify_credentials()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L175) (8 connections)
- [DefaultAdminTests](file:///Users/macbook/Documents/ProjectTracker/tests/test_auth_defaults.py#L12) (8 connections)
- [IsolatedAppFixture](file:///Users/macbook/ProjectTracker/tests/test_priority_bugs.py#L36) (8 connections)
- [create_user()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L190) (7 connections)
- [get_user_by_username()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L167) (7 connections)
- [login()](file:///Users/macbook/ProjectTracker/tracker/routes/auth_routes.py#L32) (7 connections)
- [set_user_permissions()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L219) (6 connections)
- [._create_user()](file:///Users/macbook/ProjectTracker/tests/test_auth.py#L35) (6 connections)
- [.setUp()](file:///Users/macbook/ProjectTracker/tests/test_priority_bugs.py#L37) (6 connections)
- [.test_paid_quote_and_project_cannot_be_deleted()](file:///Users/macbook/ProjectTracker/tests/test_remaining_bugs.py#L21) (6 connections)
- [.test_unpaid_deletion_preserves_other_projects_payments()](file:///Users/macbook/ProjectTracker/tests/test_remaining_bugs.py#L38) (6 connections)
- [_default_admin_config()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L56) (5 connections)
- [set_user_active()](file:///Users/macbook/ProjectTracker/tracker/auth.py#L197) (5 connections)
- [User](file:///Users/macbook/ProjectTracker/tracker/auth.py#L101) (5 connections)
- [.setUp()](file:///Users/macbook/ProjectTracker/tests/test_auth.py#L108) (5 connections)
- *... and 76 more nodes in this community*

## Class Diagram

```mermaid
classDiagram
    class User {
        +auth.py()
        +.__init__()
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
    class BootstrapPriorityTests {
        +test_priority_bugs.py()
        +.test_no_configuration_generates_unique_password_and_preserves_existing_account()
    }
    class IsolatedAppFixture {
        +test_priority_bugs.py()
        +.setUp()
        +.login()
        +.grant()
        +.snapshot()
    }
    class IsolatedPriorityTests {
        +test_priority_bugs.py()
        +.test_terms_script_and_both_editors_are_available()
        +.test_only_admin_can_delete_project_even_with_all_permissions()
        +.test_no_grants_denies_read_and_write_without_changing_data()
        +.test_each_permission_is_enforced_individually()
        +.test_import_cannot_bypass_quote_edit_permissions()
        +.test_every_scoped_quote_and_ldm_route_checks_ownership()
        +.test_payment_rejects_nonfinite_amounts_and_invalid_dates()
        +.test_quote_and_ldm_forms_reject_nonfinite_values()
        +.test_failed_request_discards_pending_writes_and_releases_lock()
    }
    class RemainingBugTests {
        +test_remaining_bugs.py()
        +.payment()
        +.test_paid_quote_and_project_cannot_be_deleted()
        +.test_unpaid_deletion_preserves_other_projects_payments()
        +.close()
        +.test_closed_projects_reject_all_project_document_mutations()
        +.test_closed_mobile_draft_reset_and_ldm_cost_api_are_guarded()
        +.test_closed_project_can_be_read_and_paid_then_reopened_to_edit()
        +.test_dashboard_and_detail_share_active_totals_and_ignore_mobile_drafts()
        +.test_catalog_decimal_comma_works_for_create_and_edit()
    }
    IsolatedPriorityTests <|-- IsolatedAppFixture
    IsolatedAppFixture --> RemainingBugTests
    IsolatedAppFixture <|-- IsolatedPriorityTests
    RemainingBugTests --> IsolatedAppFixture
```

## Relationships

- No strong cross-community connections detected

## Source Files

- [/Users/macbook/Documents/ProjectTracker/tests/test_auth_defaults.py](file:///Users/macbook/Documents/ProjectTracker/tests/test_auth_defaults.py)
- [/Users/macbook/ProjectTracker/tests/test_auth.py](file:///Users/macbook/ProjectTracker/tests/test_auth.py)
- [/Users/macbook/ProjectTracker/tests/test_priority_bugs.py](file:///Users/macbook/ProjectTracker/tests/test_priority_bugs.py)
- [/Users/macbook/ProjectTracker/tests/test_remaining_bugs.py](file:///Users/macbook/ProjectTracker/tests/test_remaining_bugs.py)
- [/Users/macbook/ProjectTracker/tracker/auth.py](file:///Users/macbook/ProjectTracker/tracker/auth.py)
- [/Users/macbook/ProjectTracker/tracker/routes/admin.py](file:///Users/macbook/ProjectTracker/tracker/routes/admin.py)
- [/Users/macbook/ProjectTracker/tracker/routes/auth_routes.py](file:///Users/macbook/ProjectTracker/tracker/routes/auth_routes.py)

## Audit Trail

- EXTRACTED: 300 (69%)
- INFERRED: 132 (31%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*