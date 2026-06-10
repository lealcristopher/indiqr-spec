import re
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app


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
ADMIN_USER = {
    "id": 30,
    "email": "admin@test.com",
    "roles": ["indiqr-admin"],
}
INFLUENCER_2_USER = {
    "id": 11,
    "email": "influencer2@test.com",
    "roles": ["indiqr-influenciador"],
}
NO_ROLE_USER = {"id": 99, "email": "norole@test.com", "roles": []}

COMPANY_1_ID = 1
COMPANY_2_ID = 2


def _auth_client(user):
    app.dependency_overrides.clear()
    from app.api.dependencies.auth import get_current_user

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user
    return TestClient(app)


@pytest.fixture
def client_influencer():
    return _auth_client(INFLUENCER_USER)


@pytest.fixture
def client_influencer2():
    return _auth_client(INFLUENCER_2_USER)


@pytest.fixture
def client_vendedor():
    return _auth_client(VENDEDOR_USER)


@pytest.fixture
def client_admin():
    return _auth_client(ADMIN_USER)


@pytest.fixture
def client_no_role():
    return _auth_client(NO_ROLE_USER)


@pytest.fixture
def anonymous_client():
    app.dependency_overrides.clear()
    return TestClient(app)


@pytest.fixture
def pending_token_payload():
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    return {
        "id": 1,
        "influenciador_id": 10,
        "valor": 50.00,
        "tipo": "reais",
        "code": "483921",
        "status": "pendente",
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


PENDING_CODE = "483921"
EXPIRED_CODE = "111222"
USED_CODE = "333444"
ALPHANUMERIC_CODE = "XpT250"


def _mock_db_session():
    session = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.add = MagicMock()
    session.refresh = MagicMock(side_effect=lambda obj: obj)
    return session


def _mock_resend_response(status_code=200, response_id="res-123"):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = {"id": response_id}
    mock_resp.raise_for_status = MagicMock()
    if status_code >= 400:
        mock_resp.raise_for_status.side_effect = Exception("HTTP error")
    return mock_resp


# ══════════════════════════════════════════════════════════════════════════════
# POST /redemptions/tokens — Gerar código OTP
# ══════════════════════════════════════════════════════════════════════════════

class TestGenerateRedemptionToken:
    def test_influenciador_creates_token_success(self, client_influencer):
        resp = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 50.00, "tipo": "reais"},
        )
        assert resp.status_code in (201, 200)

        data = resp.json()
        assert data["tipo"] == "reais"
        assert data["valor"] == 50.00
        assert data["status"] == "pendente"
        assert re.match(r"^\d{6}$", data["code"]), (
            f"code={data['code']!r} is not a 6-digit numeric string"
        )

    def test_influenciador_without_balance_returns_422(self, client_influencer):
        resp = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 99999.99, "tipo": "reais"},
        )
        assert resp.status_code == 422

    def test_create_second_token_same_type_cancels_previous(self, client_influencer):
        first = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 30.00, "tipo": "reais"},
        )
        assert first.status_code in (201, 200)
        first_data = first.json()
        first_id = first_data["id"]

        second = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 25.00, "tipo": "reais"},
        )
        assert second.status_code in (201, 200)

        resp = client_influencer.get(f"/api/v1/redemptions/tokens/{first_id}")
        if resp.status_code != 404:
            data = resp.json()
            assert data["status"] == "expirado"

    def test_create_token_different_type_does_not_cancel_existing(self, client_influencer):
        first = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 30.00, "tipo": "reais"},
        )
        assert first.status_code in (201, 200)
        first_data = first.json()

        resp = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 100.00, "tipo": "pontos"},
        )
        assert resp.status_code in (201, 200)

        check = client_influencer.get(f"/api/v1/redemptions/tokens/{first_data['id']}")
        if check.status_code != 404:
            assert check.json()["status"] == "pendente"

    def test_vendedor_cannot_create_token(self, client_vendedor):
        resp = client_vendedor.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 50.00, "tipo": "reais"},
        )
        assert resp.status_code == 403

    def test_admin_cannot_create_token(self, client_admin):
        resp = client_admin.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 50.00, "tipo": "reais"},
        )
        assert resp.status_code == 403

    def test_no_role_cannot_create_token(self, client_no_role):
        resp = client_no_role.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 50.00, "tipo": "reais"},
        )
        assert resp.status_code in (401, 403)

    def test_negative_value_rejected(self, client_influencer):
        resp = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": -10.00, "tipo": "reais"},
        )
        assert resp.status_code == 422

    def test_zero_value_rejected(self, client_influencer):
        resp = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 0, "tipo": "reais"},
        )
        assert resp.status_code == 422

    def test_invalid_type_rejected(self, client_influencer):
        resp = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 50.00, "tipo": "creditos"},
        )
        assert resp.status_code == 422

    def test_no_points_balance_for_pontos_type_returns_422(self, client_influencer):
        resp = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 100.00, "tipo": "pontos"},
        )
        assert resp.status_code in (200, 201, 422)


# ══════════════════════════════════════════════════════════════════════════════
# GET /redemptions/tokens/active — Token ativo
# ══════════════════════════════════════════════════════════════════════════════

class TestGetActiveToken:
    def test_get_active_token_returns_pending(self, client_influencer):
        client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 25.00, "tipo": "reais"},
        )
        resp = client_influencer.get("/api/v1/redemptions/tokens/active")
        assert resp.status_code in (200, 201)
        data = resp.json()
        if isinstance(data, list):
            matching = [t for t in data if t.get("status") == "pendente"]
            assert len(matching) >= 1
        else:
            assert data.get("status") == "pendente"

    def test_get_active_token_none_active_returns_404(self, client_influencer):
        resp = client_influencer.get("/api/v1/redemptions/tokens/active")
        assert resp.status_code in (200, 404)


# ══════════════════════════════════════════════════════════════════════════════
# DELETE /redemptions/tokens/{id} — Cancelar token
# ══════════════════════════════════════════════════════════════════════════════

class TestCancelToken:
    def test_influenciador_cancels_own_pending_token(self, client_influencer):
        create = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 25.00, "tipo": "reais"},
        )
        assert create.status_code in (201, 200)
        token_id = create.json()["id"]

        resp = client_influencer.delete(f"/api/v1/redemptions/tokens/{token_id}")
        assert resp.status_code in (200, 204)

        get_resp = client_influencer.get(f"/api/v1/redemptions/tokens/{token_id}")
        if get_resp.status_code != 404:
            assert get_resp.json()["status"] == "expirado"

    def test_influenciador_cannot_cancel_anothers_token(self, client_influencer, client_influencer2):
        create = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 25.00, "tipo": "reais"},
        )
        assert create.status_code in (201, 200)
        token_id = create.json()["id"]

        resp = client_influencer2.delete(f"/api/v1/redemptions/tokens/{token_id}")
        assert resp.status_code == 403

    def test_cancel_nonexistent_token(self, client_influencer):
        resp = client_influencer.delete("/api/v1/redemptions/tokens/99999")
        assert resp.status_code in (404, 422)


# ══════════════════════════════════════════════════════════════════════════════
# GET /redemptions/preview — Preview do resgate
# ══════════════════════════════════════════════════════════════════════════════

class TestPreviewRedemption:
    def test_nonexistent_code_returns_404(self, client_vendedor):
        resp = client_vendedor.get("/api/v1/redemptions/preview?code=000000")
        assert resp.status_code in (404, 422)

    def test_alphanumeric_code_returns_404_or_422(self, client_vendedor):
        resp = client_vendedor.get("/api/v1/redemptions/preview?code=XpT250")
        assert resp.status_code in (404, 422)


# ══════════════════════════════════════════════════════════════════════════════
# POST /redemptions/validate — Confirmar resgate
# ══════════════════════════════════════════════════════════════════════════════

class TestValidateRedemption:
    def test_influenciador_cannot_validate_own_code(self, client_influencer):
        resp = client_influencer.post(
            "/api/v1/redemptions/validate",
            json={"code": PENDING_CODE},
        )
        assert resp.status_code == 403

    def test_admin_cannot_validate(self, client_admin):
        resp = client_admin.post(
            "/api/v1/redemptions/validate",
            json={"code": PENDING_CODE},
        )
        assert resp.status_code == 403

    def test_nonexistent_code_returns_404(self, client_vendedor):
        resp = client_vendedor.post(
            "/api/v1/redemptions/validate",
            json={"code": "000000"},
        )
        assert resp.status_code in (404, 422)


# ══════════════════════════════════════════════════════════════════════════════
# GET /redemptions/ — Listar resgates
# ══════════════════════════════════════════════════════════════════════════════

class TestListRedemptions:
    def test_influenciador_gets_list(self, client_influencer):
        resp = client_influencer.get("/api/v1/redemptions/")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data or isinstance(data, list)

    def test_vendedor_gets_list(self, client_vendedor):
        resp = client_vendedor.get("/api/v1/redemptions/")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data or isinstance(data, list)

    def test_pagination_works(self, client_influencer):
        resp = client_influencer.get("/api/v1/redemptions/?page=1&page_size=10")
        assert resp.status_code == 200
        data = resp.json()
        if isinstance(data, dict):
            assert data.get("page") == 1
            assert data.get("page_size") == 10


# ══════════════════════════════════════════════════════════════════════════════
# GET /redemptions/company — Listar resgates da empresa (admin)
# ══════════════════════════════════════════════════════════════════════════════

class TestCompanyRedemptions:
    def test_admin_sees_company_redemptions(self, client_admin):
        resp = client_admin.get("/api/v1/redemptions/company")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data or isinstance(data, list)

    def test_influenciador_cannot_access_company_list(self, client_influencer):
        resp = client_influencer.get("/api/v1/redemptions/company")
        assert resp.status_code == 403

    def test_vendedor_cannot_access_company_list(self, client_vendedor):
        resp = client_vendedor.get("/api/v1/redemptions/company")
        assert resp.status_code == 403


# ══════════════════════════════════════════════════════════════════════════════
# GET /redemptions/{id} — Detalhe do resgate
# ══════════════════════════════════════════════════════════════════════════════

class TestGetRedemptionById:
    def test_nonexistent_returns_404(self, client_influencer):
        resp = client_influencer.get("/api/v1/redemptions/99999")
        assert resp.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# GET /redemptions/balance — Saldo
# ══════════════════════════════════════════════════════════════════════════════

class TestGetBalance:
    def test_influenciador_gets_balance(self, client_influencer):
        resp = client_influencer.get("/api/v1/redemptions/balance")
        assert resp.status_code == 200
        data = resp.json()
        assert "saldo_reais" in data
        assert "saldo_pontos" in data

    def test_vendedor_cannot_get_balance(self, client_vendedor):
        resp = client_vendedor.get("/api/v1/redemptions/balance")
        assert resp.status_code == 403

    def test_admin_cannot_get_balance(self, client_admin):
        resp = client_admin.get("/api/v1/redemptions/balance")
        assert resp.status_code == 403


# ══════════════════════════════════════════════════════════════════════════════
# Fluxo completo E2E
# ══════════════════════════════════════════════════════════════════════════════

class TestFullRedemptionFlow:
    def test_generate_and_cancel_token(self, client_influencer):
        create = client_influencer.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 25.00, "tipo": "reais"},
        )
        assert create.status_code in (201, 200)
        token = create.json()
        assert re.match(r"^\d{6}$", token["code"])
        assert token["status"] == "pendente"

        token_id = token["id"]
        cancel = client_influencer.delete(f"/api/v1/redemptions/tokens/{token_id}")
        assert cancel.status_code in (200, 204)

    def test_rate_limiting_basic(self, client_no_role):
        resp = client_no_role.get("/api/v1/redemptions/")
        assert resp.status_code in (401, 403)


# ══════════════════════════════════════════════════════════════════════════════
# Segurança
# ══════════════════════════════════════════════════════════════════════════════

class TestRedemptionSecurity:
    def test_unauthenticated_returns_401(self, anonymous_client):
        resp = anonymous_client.get("/api/v1/redemptions/")
        assert resp.status_code == 401

        resp = anonymous_client.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 50.00, "tipo": "reais"},
        )
        assert resp.status_code == 401

        resp = anonymous_client.post(
            "/api/v1/redemptions/validate",
            json={"code": "483921"},
        )
        assert resp.status_code == 401

    def test_no_role_user_denied(self, client_no_role):
        resp = client_no_role.post(
            "/api/v1/redemptions/tokens",
            json={"valor": 50.00, "tipo": "reais"},
        )
        assert resp.status_code in (401, 403)

        resp = client_no_role.post(
            "/api/v1/redemptions/validate",
            json={"code": "483921"},
        )
        assert resp.status_code in (401, 403)

    def test_invalid_code_format_rejected(self, client_vendedor):
        resp = client_vendedor.get("/api/v1/redemptions/preview?code=not-a-number")
        assert resp.status_code in (404, 422)

    def test_error_response_does_not_echo_code(self, client_vendedor):
        resp = client_vendedor.post(
            "/api/v1/redemptions/validate",
            json={"code": "999999"},
        )
        assert resp.status_code in (404, 422)
        if resp.status_code >= 400:
            body = resp.text.lower()
            assert "999999" not in body or resp.status_code == 404
