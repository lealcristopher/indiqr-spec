from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


ADMIN_USER = {
    "id": 30,
    "email": "admin@test.com",
    "roles": ["indiqr-admin"],
}
INFLUENCER_USER = {
    "id": 10,
    "email": "influencer@test.com",
    "roles": ["indiqr-influenciador"],
}
VENDEDOR_USER = {
    "id": 20,
    "email": "vendedor@test.com",
    "roles": ["indiqr-vendedor"],
}
NO_ROLE_USER = {"id": 99, "email": "norole@test.com", "roles": []}


def _auth_client(user):
    app.dependency_overrides.clear()
    from app.api.dependencies.auth import get_current_user

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user
    return TestClient(app)


@pytest.fixture
def client_admin():
    return _auth_client(ADMIN_USER)


@pytest.fixture
def client_influencer():
    return _auth_client(INFLUENCER_USER)


@pytest.fixture
def client_vendedor():
    return _auth_client(VENDEDOR_USER)


@pytest.fixture
def client_no_role():
    return _auth_client(NO_ROLE_USER)


@pytest.fixture
def anonymous_client():
    app.dependency_overrides.clear()
    return TestClient(app)


CONSENT_VERSION = "v2.0"


# ══════════════════════════════════════════════════════════════════════════════
# GET /user/me — consentiu_privacy_policy é false por default (opt-in)
# ══════════════════════════════════════════════════════════════════════════════

class TestConsentIsOptIn:
    def test_consentiu_privacy_policy_false_by_default(self, client_admin):
        resp = client_admin.get("/api/v1/user/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["consentiu_privacy_policy"] is False

    def test_consent_fields_present_in_user_response(self, client_admin):
        resp = client_admin.get("/api/v1/user/me")
        assert resp.status_code == 200
        data = resp.json()
        assert "consentiu_privacy_policy" in data
        assert "consentiu_privacy_policy_at" in data
        assert "privacy_policy_version" in data


# ══════════════════════════════════════════════════════════════════════════════
# PUT /user/me/consent — Registrar consentimento
# ══════════════════════════════════════════════════════════════════════════════

class TestPutConsent:
    def test_put_consent_success(self, client_admin):
        resp = client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["consentiu_privacy_policy"] is True
        assert data["privacy_policy_version"] == CONSENT_VERSION
        assert "consentiu_privacy_policy_at" in data

    def test_put_consent_idempotent(self, client_influencer):
        first = client_influencer.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        assert first.status_code == 200

        second = client_influencer.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        assert second.status_code == 200

    def test_put_consent_missing_version(self, client_admin):
        resp = client_admin.put(
            "/api/v1/user/me/consent",
            json={},
        )
        assert resp.status_code == 422

    def test_put_consent_empty_version(self, client_admin):
        resp = client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": ""},
        )
        assert resp.status_code == 422

    def test_influenciador_can_consent(self, client_influencer):
        resp = client_influencer.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        assert resp.status_code == 200
        assert resp.json()["consentiu_privacy_policy"] is True

    def test_vendedor_can_consent(self, client_vendedor):
        resp = client_vendedor.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        assert resp.status_code == 200
        assert resp.json()["consentiu_privacy_policy"] is True

    def test_no_role_user_can_consent(self, client_no_role):
        resp = client_no_role.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        assert resp.status_code == 200
        assert resp.json()["consentiu_privacy_policy"] is True

    def test_consent_updates_user_me(self, client_admin):
        resp = client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        assert resp.status_code == 200

        me = client_admin.get("/api/v1/user/me")
        assert me.status_code == 200
        assert me.json()["consentiu_privacy_policy"] is True
        assert me.json()["privacy_policy_version"] == CONSENT_VERSION

    def test_consent_with_different_version_updates(self, client_admin):
        first = client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": "v1.0"},
        )
        assert first.status_code == 200

        second = client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": "v2.0"},
        )
        assert second.status_code == 200
        assert second.json()["privacy_policy_version"] == "v2.0"


# ══════════════════════════════════════════════════════════════════════════════
# DELETE /user/me/consent — Revogar consentimento
# ══════════════════════════════════════════════════════════════════════════════

class TestDeleteConsent:
    def test_delete_consent_success(self, client_admin):
        client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        resp = client_admin.delete("/api/v1/user/me/consent")
        assert resp.status_code == 200
        data = resp.json()
        assert data["consentiu_privacy_policy"] is False
        assert "revoked_at" in data

    def test_delete_consent_returns_previous_version(self, client_admin):
        client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        resp = client_admin.delete("/api/v1/user/me/consent")
        assert resp.status_code == 200
        assert resp.json().get("previous_version") == CONSENT_VERSION

    def test_delete_consent_idempotent(self, client_admin):
        client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        first = client_admin.delete("/api/v1/user/me/consent")
        assert first.status_code == 200

        second = client_admin.delete("/api/v1/user/me/consent")
        assert second.status_code == 200
        assert second.json()["consentiu_privacy_policy"] is False

    def test_delete_consent_updates_user_me(self, client_admin):
        client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        client_admin.delete("/api/v1/user/me/consent")

        me = client_admin.get("/api/v1/user/me")
        assert me.status_code == 200
        assert me.json()["consentiu_privacy_policy"] is False

    def test_influenciador_can_revoke(self, client_influencer):
        client_influencer.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        resp = client_influencer.delete("/api/v1/user/me/consent")
        assert resp.status_code == 200
        assert resp.json()["consentiu_privacy_policy"] is False

    def test_vendedor_can_revoke(self, client_vendedor):
        client_vendedor.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        resp = client_vendedor.delete("/api/v1/user/me/consent")
        assert resp.status_code == 200

    def test_no_role_user_can_revoke(self, client_no_role):
        client_no_role.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        resp = client_no_role.delete("/api/v1/user/me/consent")
        assert resp.status_code == 200

    def test_reconsent_after_revoke(self, client_admin):
        client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": "v1.0"},
        )
        client_admin.delete("/api/v1/user/me/consent")

        resp = client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": "v2.0"},
        )
        assert resp.status_code == 200
        assert resp.json()["consentiu_privacy_policy"] is True
        assert resp.json()["privacy_policy_version"] == "v2.0"


# ══════════════════════════════════════════════════════════════════════════════
# RBAC — Todos os usuários autenticados podem consentir/revogar
# ══════════════════════════════════════════════════════════════════════════════

class TestConsentRBAC:
    def test_unauthenticated_consent_returns_401(self, anonymous_client):
        resp = anonymous_client.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        assert resp.status_code == 401

    def test_unauthenticated_revoke_returns_401(self, anonymous_client):
        resp = anonymous_client.delete("/api/v1/user/me/consent")
        assert resp.status_code == 401

    def test_consent_uses_authenticated_user(self, client_admin, client_influencer):
        client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": "v-admin"},
        )
        admin_me = client_admin.get("/api/v1/user/me")
        assert admin_me.json()["privacy_policy_version"] == "v-admin"

        client_influencer.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": "v-influencer"},
        )
        influencer_me = client_influencer.get("/api/v1/user/me")
        assert influencer_me.json()["privacy_policy_version"] == "v-influencer"

        admin_check = client_admin.get("/api/v1/user/me")
        assert admin_check.json()["privacy_policy_version"] == "v-admin"


# ══════════════════════════════════════════════════════════════════════════════
# Trilha de Auditoria
# ══════════════════════════════════════════════════════════════════════════════

class TestAuditTrail:
    def test_audit_log_created_on_grant(self, client_admin):
        resp = client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        assert resp.status_code == 200

    def test_audit_log_created_on_revoke(self, client_admin):
        client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        resp = client_admin.delete("/api/v1/user/me/consent")
        assert resp.status_code == 200

    def test_audit_log_stores_correct_version(self, client_admin):
        version = "v9.9.9-test"
        client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": version},
        )
        me = client_admin.get("/api/v1/user/me")
        assert me.json()["privacy_policy_version"] == version


# ══════════════════════════════════════════════════════════════════════════════
# Fluxo completo E2E
# ══════════════════════════════════════════════════════════════════════════════

class TestFullConsentFlow:
    def test_full_consent_lifecycle(self, client_admin):
        me = client_admin.get("/api/v1/user/me")
        assert me.status_code == 200
        assert me.json()["consentiu_privacy_policy"] is False

        consent = client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        assert consent.status_code == 200
        assert consent.json()["consentiu_privacy_policy"] is True
        assert consent.json()["privacy_policy_version"] == CONSENT_VERSION

        me2 = client_admin.get("/api/v1/user/me")
        assert me2.json()["consentiu_privacy_policy"] is True

        revoke = client_admin.delete("/api/v1/user/me/consent")
        assert revoke.status_code == 200
        assert revoke.json()["consentiu_privacy_policy"] is False
        assert revoke.json().get("previous_version") == CONSENT_VERSION

        me3 = client_admin.get("/api/v1/user/me")
        assert me3.json()["consentiu_privacy_policy"] is False

        new_consent = client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": "v3.0"},
        )
        assert new_consent.status_code == 200
        assert new_consent.json()["consentiu_privacy_policy"] is True
        assert new_consent.json()["privacy_policy_version"] == "v3.0"

    def test_consent_race_condition_same_version(self, client_admin):
        for _ in range(5):
            resp = client_admin.put(
                "/api/v1/user/me/consent",
                json={"privacy_policy_version": CONSENT_VERSION},
            )
            assert resp.status_code == 200

        me = client_admin.get("/api/v1/user/me")
        assert me.json()["consentiu_privacy_policy"] is True


# ══════════════════════════════════════════════════════════════════════════════
# Segurança
# ══════════════════════════════════════════════════════════════════════════════

class TestConsentSecurity:
    def test_unauthenticated_cannot_access_consent(self, anonymous_client):
        resp = anonymous_client.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": CONSENT_VERSION},
        )
        assert resp.status_code == 401

        resp = anonymous_client.delete("/api/v1/user/me/consent")
        assert resp.status_code == 401

    def test_put_without_body_returns_422(self, client_admin):
        resp = client_admin.put("/api/v1/user/me/consent")
        assert resp.status_code in (422, 415)

    def test_large_version_string_accepted(self, client_admin):
        version = "v" + ("x" * 100)
        resp = client_admin.put(
            "/api/v1/user/me/consent",
            json={"privacy_policy_version": version},
        )
        assert resp.status_code == 200
        assert resp.json()["privacy_policy_version"] == version
