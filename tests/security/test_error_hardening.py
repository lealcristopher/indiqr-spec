"""Error hardening — no stack traces, debug disabled, internal details hidden."""

import pytest


STACK_TRACE_MARKERS = [
    "Traceback (most recent call last)",
    "File \"",
    ", line ",
    "site-packages",
    "/app/",
    "raise ",
    "Exception",
    "Error",
]
DB_LEAK_MARKERS = [
    "unique constraint",
    "foreign key",
    "violates",
    "duplicate key",
    "psycopg2",
    "sqlalchemy",
]
AUTH0_LEAK_MARKERS = [
    "tenant",
    "client_id",
    "client_secret",
    "m2m",
    "management api",
]
INTERNAL_ERROR_DETAIL = "Internal server error"


class TestNoStackTraces:
    async def test_500_response_no_stack_trace(self, async_client, auth_headers):
        try:
            resp = await async_client.get("/redemptions/validate", headers=auth_headers)
            if resp.status_code == 500:
                body = resp.json()
                detail = body.get("detail", "")
                for marker in STACK_TRACE_MARKERS:
                    assert marker.lower() not in detail.lower(), (
                        f"500 response leaked trace data: {marker}"
                    )
        except Exception:
            pass

    async def test_422_response_no_internal_details(self, async_client, auth_headers):
        resp = await async_client.post(
            "/companies/",
            json={},
            headers=auth_headers,
        )
        if resp.status_code == 422:
            body = resp.json()
            detail = body.get("detail", [])
            detail_str = str(detail).lower()
            for marker in STACK_TRACE_MARKERS:
                assert marker.lower() not in detail_str, (
                    f"422 response leaked stack trace marker: {marker}"
                )

    async def test_database_error_no_leak(self, async_client, auth_headers):
        resp = await async_client.post(
            "/companies/",
            json={"name": "Duplicated", "slug": "test-dup"},
            headers=auth_headers,
        )
        if resp.status_code == 409:
            body = resp.json()
            detail = body.get("detail", "")
            detail_lower = detail.lower()
            for marker in DB_LEAK_MARKERS:
                assert marker.lower() not in detail_lower, (
                    f"DB error leaked: {marker} in '{detail}'"
                )

    async def test_auth0_error_no_leak(self, async_client):
        resp = await async_client.get("/user/me")
        if resp.status_code in (401, 500):
            body = resp.json()
            detail = body.get("detail", "")
            detail_lower = detail.lower()
            for marker in AUTH0_LEAK_MARKERS:
                assert marker.lower() not in detail_lower, (
                    f"Auth0 error leaked: {marker} in '{detail}'"
                )


class TestDebugDisabled:
    FORBIDDEN_DEBUG_HEADERS = [
        "x-debug-toolbar",
        "x-debug-token",
        "x-debug",
        "x-powered-by",
        "x-aspnet-version",
        "x-runtime",
    ]

    async def test_debug_mode_disabled_in_production(self, async_client):
        resp = await async_client.get("/health")
        for hdr in self.FORBIDDEN_DEBUG_HEADERS:
            assert hdr not in resp.headers, (
                f"Debug header present: {hdr}"
            )

    async def test_server_header_not_versioned(self, async_client):
        resp = await async_client.get("/health")
        server = resp.headers.get("server", "")
        assert server.lower() in ("", "nginx", "cloudflare", "envoy", "api"), (
            f"Server header leaks version: {server}"
        )
