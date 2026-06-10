# Test Coverage Specification — IndiQR

> Last updated: 2026-06-10 by CTO / [IND-41](/IND/issues/IND-41)
>
> P2 test specifications completed:
> - [membership-requests.md](membership-requests.md) — membership request E2E
> - [shop-media.md](shop-media.md) — shop media endpoints E2E
> - [security.md](security.md) — security test layer
> - `make test-contract` — local Schemathesis target (see repo `Makefile`)

## Coverage Summary (current)

| Layer | Files | Test Functions | Coverage Assessment |
|-------|-------|---------------|-------------------|
| Unit | 5 | 59 | Campaigns, Companies, Conversions (calculator), Redemptions (OTP), Schemas — solid |
| Integration | 5 | 102 | All 5 repositories covered; DB queries, joins, constraints verified |
| E2E | 6 | 99 | All major domain endpoints covered with role-based clients |
| Smoke | 1 | 5 | Basic RBAC smoke tests against live API |

**Total: 17 test files, 265 test functions (incl. smoke)**

## GAP Analysis

### Critical Gaps (untested endpoints/services)

| Priority | Area | Gap |
|----------|------|-----|
| P1 | `GET /companies/{id}/stats` | No tests. Returns aggregate conversion stats. |
| P1 | `PATCH /companies/{id}` | No tests. Admin updates company name. |
| P1 | `GET /campaigns/public/{short_token}` | No tests. Public campaign preview endpoint. |
| P1 | `GET /conversions/preview` | No tests. Preview conversion before validation. |
| P1 | `qrcode_service.py` | No dedicated tests. Token generation and QR image creation. |
| P1 | `card_pdf_service.py` | No dedicated tests. PDF generation with QR embedding. |
| P1 | `email_service.py` | No dedicated tests. 11 email types, critical notification path. |
| P1 | `auth0_service.py` | No dedicated tests. Role assignment/revocation via Auth0 API. |

### Medium Gaps

| Priority | Area | Gap |
|----------|------|-----|
| P2 | Membership Request APIs (4 endpoints) | Spec: [membership-requests.md](membership-requests.md) — full flow + decline + cross-company |
| P2 | `GET /redemptions/tokens/active` | No tests. Active token lookup. |
| P2 | `GET /redemptions/company` | No tests. Company-scoped resgate listing. |
| P2 | Shop media endpoints (6 endpoints) | Spec: [shop-media.md](shop-media.md) — logo, hero, category, product, gallery |
| P2 | `GET /shop/mine` | Spec: [shop-media.md](shop-media.md) — included in shop flow |
| P2 | `GET /user/me` | No tests. User profile endpoint. |

### Missing Test Categories

| Priority | Category | Gap |
|----------|------|-----|
| P2 | Security tests | Spec: [security.md](security.md) — OWASP, IDOR, JWT, race conditions, token leakage |
| P2 | Contract tests (local) | Spec: `make test-contract` in repo `Makefile` — local Schemathesis |
| P2 | Error path coverage | Many services lack edge-case unit tests (null handling, concurrent access). |
| P3 | Load/stress tests | No performance baseline or load profile tests. |
| P3 | UI E2E tests | No frontend e2e tests (Selenium/Playwright). |

---

## Proposed New Tests

### 1. Companies — Unit Tests (`tests/unit/test_company_service.py`)

- [ ] `test_get_company_stats_returns_aggregates` — verify correct sums and counts
- [ ] `test_get_company_stats_empty_company` — returns zeros, not error
- [ ] `test_get_company_stats_non_member_blocked` — 403 for non-member
- [ ] `test_update_company_success` — name update returns updated company
- [ ] `test_update_company_not_found` — 404 for nonexistent company
- [ ] `test_update_company_non_admin_blocked` — 403 for non-admin member
- [ ] `test_request_membership_success` — creates pending request, notifies admins
- [ ] `test_request_membership_already_member` — 409 if already member
- [ ] `test_request_membership_duplicate_pending` — 409 if duplicate pending request
- [ ] `test_accept_membership_request_success` — admin accepts, creates member, assigns role
- [ ] `test_accept_membership_request_invalid_token` — 404
- [ ] `test_accept_membership_request_non_admin_blocked` — 403
- [ ] `test_decline_membership_request_success` — admin declines, emails requester
- [ ] `test_decline_membership_request_optional_message` — decline with message
- [ ] `test_provision_default_company_idempotent` — second call returns existing company

### 2. Companies — E2E Tests (`tests/e2e/test_companies_api.py`)

- [ ] `test_get_company_stats` — endpoint returns stats with correct data after conversions
- [ ] `test_update_company_name` — PATCH updates name, returns updated company
- [ ] `test_membership_request_full_lifecycle` — request → preview → accept → member appears
- [ ] `test_membership_request_decline` — request → decline → request no longer pending

### 3. Campaigns — Unit Tests (`tests/unit/test_campaign_service.py`)

- [ ] `test_get_campaign_public_valid_token` — public endpoint returns campaign preview
- [ ] `test_get_campaign_public_invalid_token` — 404 for nonexistent short token
- [ ] `test_list_campaigns_pagination` — verify cursor/offset pagination

### 4. Campaigns — E2E Tests (`tests/e2e/test_campaigns_api.py`)

- [ ] `test_get_public_campaign_by_short_token` — unauthenticated public preview
- [ ] `test_list_campaigns_pagination` — page 1, page 2, page_size

### 5. Conversions — Unit Tests (`tests/unit/test_conversion_service.py`)

- [ ] `test_validate_with_inactive_campaign` — raises 422
- [ ] `test_validate_with_zero_valor_bruto` — raises 422
- [ ] `test_validate_credits_wallet_reais` — verify wallet balance increased
- [ ] `test_validate_credits_wallet_pontos` — verify pontos wallet increased for usa_pontos
- [ ] `test_list_conversions_admin_sees_all` — admin scope
- [ ] `test_list_conversions_influenciador_sees_own` — influencer scope
- [ ] `test_list_conversions_vendedor_sees_own` — seller scope

### 6. Conversions — E2E Tests (`tests/e2e/test_conversions_api.py`)

- [ ] `test_preview_conversion_valid_token` — preview returns campaign+QRCode info
- [ ] `test_preview_conversion_invalid_token` — 404 for bad token
- [ ] `test_preview_conversion_inactive_qrcode` — 404
- [ ] `test_conversion_idempotency` — same QRCode cannot validate twice for same scan
- [ ] `test_wallet_credited_after_conversion` — verify saldo_reais incremented

### 7. Redemptions — E2E Tests (`tests/e2e/test_redemptions_api.py`)

> Spec: [redemptions.md](redemptions.md) § Testes for detailed redemption coverage.

- [ ] `test_get_active_token` — GET /tokens/active returns current pending token
- [ ] `test_get_active_token_no_active` — returns empty/null when no pending token
- [ ] `test_list_resgates_company` — GET /company returns company-scoped resgates for admin

### 8. Shop — E2E Tests (`tests/e2e/test_shop_api.py`)

> Full spec: [shop-media.md](shop-media.md). Summary:

- [ ] `test_get_my_shop` — GET /mine returns admin's shop
- [ ] `test_get_my_shop_no_shop` — 404 when admin has no shop
- [ ] `test_upload_logo` — POST with image file updates logo
- [ ] `test_upload_hero` — POST with image file updates hero
- [ ] `test_upload_logo_invalid_type` — 422 for non-image file
- [ ] `test_upload_category_image` — POST image to category
- [ ] `test_upload_product_image` — POST main image to product
- [ ] `test_upload_product_gallery_image` — POST gallery image
- [ ] `test_delete_product_gallery_image` — DELETE gallery image
- [ ] `test_reorder_product_gallery` — PUT reorder
- [ ] `test_shop_full_media_flow` — complete shop lifecycle

### 9. Security Tests (new file: `tests/security/`)

> Full spec: [security.md](security.md). Structure:

- `tests/security/test_token_handling.py` — OTP/short token leakage (3 tests)
- `tests/security/test_error_hardening.py` — no stack traces, debug disabled (6 tests)
- `tests/security/test_idor.py` — cross-company IDOR + enumeration resistance (12 tests)
- `tests/security/test_jwt_validation.py` — expiry, audience, signature (10 tests)
- `tests/security/test_race_conditions.py` — concurrent validate, token gen, invite accept (5 tests)
- `tests/security/test_input_sanitization.py` — SQL injection, XSS, large payloads (9 tests)
- `tests/security/test_cors_headers.py` — CORS preflight + disallowed origins (3 tests)

### 10. New Service Tests

#### `tests/unit/test_qrcode_service.py`
- [ ] `test_generate_qrcode_image_returns_bytes` — output is PNG bytes
- [ ] `test_generate_qrcode_image_size` — output is non-empty
- [ ] `test_generate_short_token_length` — exactly 6 characters
- [ ] `test_generate_short_token_alphanumeric` — only [A-Za-z0-9]
- [ ] `test_generate_short_token_unique` — two calls produce different tokens
- [ ] `test_create_qrcode_for_campaign_active` — QRCode created with active=True

#### `tests/unit/test_card_pdf_service.py`
- [ ] `test_generate_card_pdf_returns_bytes` — output is PDF bytes
- [ ] `test_generate_card_pdf_valid_pdf` — output is valid PDF (starts with %PDF)
- [ ] `test_generate_card_pdf_contains_campaign_name` — text appears in PDF
- [ ] `test_generate_card_pdf_contains_short_token` — short token rendered

#### `tests/unit/test_email_service.py`
- [ ] `test_send_company_invite_calls_resend` — HTTP request to Resend API dispatched
- [ ] `test_send_campaign_invite_contains_accept_url` — email body includes accept link
- [ ] `test_send_campaign_invite_contains_decline_url` — email body includes decline link
- [ ] `test_email_send_failure_handled` — Resend API error handled gracefully (logged, no crash)
- [ ] `test_all_email_types_render_html` — each template produces valid HTML

### 11. Quality & Contract Tests

- [x] `make test-contract` target — run Schemathesis locally (committed to repo `Makefile`)
- [x] `make lint-oa` — run Spectral as build step (committed to repo `Makefile`)
- [x] `make validate-spec` — OpenAPI structural validation (committed to repo `Makefile`)
- [ ] OpenAPI lint check in CI — run Spectral as build step (not just staging)
- [ ] Test coverage reporting — add `pytest-cov` to requirements, enforce minimum threshold

---

## Layer Strategy

### Unit Tests (`tests/unit/`)
- Pure mock, no database
- Test service-layer business logic and edge cases
- Every service must have a unit test file
- Cover all public methods including error paths

### Integration Tests (`tests/integration/`)
- Real PostgreSQL with rollback per test
- Test repository SQL queries, joins, constraints, uniqueness
- Verify data integrity after complex operations (wallets, soft-deletes)

### E2E Tests (`tests/e2e/`)
- FastAPI TestClient with dependency overrides for auth
- Test full HTTP request/response lifecycle
- Cover RBAC: every endpoint tested with authorized + unauthorized roles
- Cover complete business flows end-to-end

### Security Tests (`tests/security/`)
- New test layer focused on OWASP top-10, IDOR, token handling
- Rate limiter interaction tests
- Input validation and sanitization

### Contract Tests
- Schemathesis against OpenAPI spec
- Run locally and in CI (not just staging)

---

## Success Criteria for IND-38

1. [x] Coverage report consolidated (this document)
2. [x] All identified gaps categorized with priority
3. [x] New test proposals listed per service/domain
4. [x] This specification committed to `indiqr-spec/behavior/tests.md`
5. [x] Child issues created for P1 and P2 implementation

## P2 Implementation Progress (IND-41)

| Area | Spec Document | Status |
|------|-------------|--------|
| Membership Requests E2E | [membership-requests.md](membership-requests.md) | Spec complete |
| Shop Media E2E | [shop-media.md](shop-media.md) | Spec complete |
| Redemptions E2E | [redemptions.md](redemptions.md) § Testes | Spec complete (P1) |
| Security Tests | [security.md](security.md) | Spec complete |
| Contract Tests | `Makefile` (`test-contract`, `lint-oa`) | Committed |
| Implementation | `api-indiqr` repo | Pending child issues |
