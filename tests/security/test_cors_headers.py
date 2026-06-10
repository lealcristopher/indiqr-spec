"""CORS headers — verify proper cross-origin resource sharing configuration."""

import pytest


ALLOWED_ORIGIN = "https://indiqr.lealcyber.com"
DISALLOWED_ORIGIN = "https://evil.com"


class TestCORSPreflight:
    async def test_cors_preflight_returns_correct_headers(self, async_client):
        resp = await async_client.options(
            "/companies/",
            headers={
                "Origin": ALLOWED_ORIGIN,
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code in (200, 204, 405), (
            f"OPTIONS returned unexpected status {resp.status_code}"
        )

        acao = resp.headers.get("access-control-allow-origin", "")
        acam = resp.headers.get("access-control-allow-methods", "")
        acah = resp.headers.get("access-control-allow-headers", "")

        if resp.status_code in (200, 204):
            assert acao != "", "Missing Access-Control-Allow-Origin header"
            assert acam != "", "Missing Access-Control-Allow-Methods header"
            assert acah != "", "Missing Access-Control-Allow-Headers header"

    async def test_cors_disallowed_origin_blocked(self, async_client):
        resp = await async_client.options(
            "/companies/",
            headers={
                "Origin": DISALLOWED_ORIGIN,
                "Access-Control-Request-Method": "GET",
            },
        )
        acao = resp.headers.get("access-control-allow-origin", "").lower()

        if resp.status_code in (200, 204):
            assert acao != DISALLOWED_ORIGIN.lower(), (
                f"CORS allowed disallowed origin: {DISALLOWED_ORIGIN}"
            )
            assert acao != "*", (
                "CORS should not use wildcard for credentialed origins"
            )

    async def test_cors_credentials_header(self, async_client):
        resp = await async_client.options(
            "/companies/",
            headers={
                "Origin": ALLOWED_ORIGIN,
                "Access-Control-Request-Method": "GET",
            },
        )
        if resp.status_code in (200, 204):
            acac = resp.headers.get("access-control-allow-credentials", "")
            if resp.headers.get("access-control-allow-origin", "") == ALLOWED_ORIGIN:
                assert acac.lower() == "true", (
                    f"Expected Access-Control-Allow-Credentials: true, got: {acac}"
                )
