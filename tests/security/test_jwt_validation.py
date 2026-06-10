"""JWT Validation — token expiry, audience, issuer, signature, and malformed tokens."""

import time

import pytest
from jose import jwt as jose_jwt


TOKEN_EXPIRED_MSG = "token has expired"
TOKEN_INVALID_MSG = "invalid token"
TOKEN_AUDIENCE_MSG = "invalid audience"
TOKEN_ISSUER_MSG = "invalid issuer"


def _build_token(
    local_jwks_secret,
    sub="auth0|test-user",
    roles=None,
    exp=None,
    aud="https://indiqr-api.lealcyber.com",
    iss="https://indiqr-dev.us.auth0.com/",
):
    if roles is None:
        roles = ["admin"]
    if exp is None:
        exp = int(time.time()) + 3600
    payload = {
        "sub": sub,
        "iss": iss,
        "aud": aud,
        "iat": int(time.time()),
        "exp": exp,
        "azp": "test-client-id",
        "scope": "openid profile email",
        "https://indiqr.lealcyber.com/roles": roles,
    }
    return jose_jwt.encode(payload, local_jwks_secret, algorithm="HS256")


class TestTokenExpiration:
    async def test_expired_token_returns_401(self, async_client, local_jwks_secret):
        token = _build_token(
            local_jwks_secret, exp=int(time.time()) - 3600
        )
        headers = {"Authorization": f"Bearer {token}"}
        resp = await async_client.get("/user/me", headers=headers)
        assert resp.status_code == 401, (
            f"Expected 401 for expired token, got {resp.status_code}"
        )

    async def test_expired_token_specific_message(self, async_client, local_jwks_secret):
        token = _build_token(
            local_jwks_secret, exp=int(time.time()) - 3600
        )
        headers = {"Authorization": f"Bearer {token}"}
        resp = await async_client.get("/user/me", headers=headers)
        body = resp.json()
        detail = body.get("detail", "")
        assert "expired" in detail.lower() or "expir" in detail.lower(), (
            f"Expected expired message, got: {detail}"
        )


class TestInvalidAudience:
    async def test_wrong_audience_returns_401(self, async_client, local_jwks_secret):
        token = _build_token(
            local_jwks_secret,
            aud="https://outro-servico.lealcyber.com",
        )
        headers = {"Authorization": f"Bearer {token}"}
        resp = await async_client.get("/user/me", headers=headers)
        assert resp.status_code == 401, (
            f"Expected 401 for wrong audience, got {resp.status_code}"
        )

    async def test_missing_audience_returns_401(self, async_client, local_jwks_secret):
        payload = {
            "sub": "auth0|test",
            "iss": "https://indiqr-dev.us.auth0.com/",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
            "https://indiqr.lealcyber.com/roles": ["admin"],
        }
        token = jose_jwt.encode(payload, local_jwks_secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}
        resp = await async_client.get("/user/me", headers=headers)
        assert resp.status_code == 401, (
            f"Expected 401 for missing audience, got {resp.status_code}"
        )


class TestInvalidIssuer:
    async def test_wrong_issuer_returns_401(self, async_client, local_jwks_secret):
        token = _build_token(
            local_jwks_secret,
            iss="https://wrong-issuer.auth0.com/",
        )
        headers = {"Authorization": f"Bearer {token}"}
        resp = await async_client.get("/user/me", headers=headers)
        assert resp.status_code == 401, (
            f"Expected 401 for wrong issuer, got {resp.status_code}"
        )


class TestMissingRoles:
    async def test_missing_roles_claim_returns_403(self, async_client, local_jwks_secret):
        payload = {
            "sub": "auth0|test",
            "iss": "https://indiqr-dev.us.auth0.com/",
            "aud": "https://indiqr-api.lealcyber.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        }
        token = jose_jwt.encode(payload, local_jwks_secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}
        resp = await async_client.get("/user/me", headers=headers)
        assert resp.status_code == 200, (
            f"User endpoint should return 200 even without roles, got {resp.status_code}"
        )
        resp = await async_client.get("/companies/", headers=headers)
        assert resp.status_code in (401, 403), (
            f"Expected 401 or 403 for missing roles on protected endpoint, got {resp.status_code}"
        )


class TestMalformedToken:
    async def test_malformed_token_returns_401(self, async_client):
        headers = {"Authorization": "Bearer not-a-jwt"}
        resp = await async_client.get("/user/me", headers=headers)
        assert resp.status_code == 401, (
            f"Expected 401 for malformed token, got {resp.status_code}"
        )

    async def test_empty_token_returns_401(self, async_client):
        headers = {"Authorization": "Bearer "}
        resp = await async_client.get("/user/me", headers=headers)
        assert resp.status_code == 401, (
            f"Expected 401 for empty token, got {resp.status_code}"
        )

    async def test_no_auth_header_returns_401(self, async_client):
        resp = await async_client.get("/user/me")
        assert resp.status_code in (401, 403), (
            f"Expected 401 or 403 for missing auth header, got {resp.status_code}"
        )


class TestSignatureTampering:
    async def test_tampered_signature_returns_401(self, async_client, local_jwks_secret):
        token = _build_token(local_jwks_secret)
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        headers = {"Authorization": f"Bearer {tampered}"}
        resp = await async_client.get("/user/me", headers=headers)
        assert resp.status_code == 401, (
            f"Expected 401 for tampered signature, got {resp.status_code}"
        )
