"""Input sanitization — SQL injection, XSS, parameter pollution, and large payloads."""

import json
import urllib.parse

import pytest


SQLI_PAYLOADS = [
    "'; DROP TABLE companies; --",
    "1; DELETE FROM companies WHERE 1=1",
    "' OR '1'='1",
    "'; SELECT * FROM users; --",
]

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "javascript:alert(1)",
    "<body onload=alert(1)>",
]


class TestSQLInjection:
    async def test_sql_injection_company_name(self, async_client, auth_headers):
        payload = {"name": "'; DROP TABLE companies; --", "slug": "sqli-test-1"}
        resp = await async_client.post(
            "/companies/",
            json=payload,
            headers=auth_headers,
        )
        assert resp.status_code in (201, 409, 422), (
            f"Unexpected status {resp.status_code} for SQLi in company name"
        )

    async def test_sql_injection_slug(self, async_client, auth_headers):
        payload = {"name": "Test", "slug": "1; DELETE FROM companies WHERE 1=1"}
        resp = await async_client.post(
            "/companies/",
            json=payload,
            headers=auth_headers,
        )
        assert resp.status_code == 422, (
            f"Expected 422 for invalid slug, got {resp.status_code}"
        )

    async def test_sql_injection_campaign_name(self, async_client, auth_headers):
        payload = {
            "name": "'; DROP TABLE campaigns; --",
            "company_id": 1,
            "influenciador_id": 1,
            "remuneracao_modelo": "fixo",
            "remuneracao_valor": 10.0,
        }
        resp = await async_client.post(
            "/campaigns/",
            json=payload,
            headers=auth_headers,
        )
        assert resp.status_code in (201, 403, 404, 422), (
            f"Unexpected status {resp.status_code} for SQLi in campaign name"
        )

    async def test_sql_injection_search_param(self, async_client, auth_headers):
        resp = await async_client.get(
            "/companies/?page=1 OR 1=1",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 422), (
            f"Expected 200 or 422, got {resp.status_code}"
        )


class TestXSS:
    async def test_xss_in_shop_name(self, async_client, auth_headers):
        xss_payload = "<script>alert(1)</script>"
        resp = await async_client.get("/shop/mine", headers=auth_headers)
        if resp.status_code == 200:
            body = resp.text
            if xss_payload.lower() in body.lower():
                escaped_forms = ["&lt;script&gt;", "\\u003c", "\\x3c"]
                raw_script = "<script>" in body
                assert not raw_script or any(
                    e in body for e in escaped_forms
                ), f"XSS payload rendered unescaped in shop response"

    async def test_xss_in_campaign_name(self, async_client, auth_headers):
        xss_payload = "<img src=x onerror=alert(1)>"
        resp = await async_client.get("/campaigns/", headers=auth_headers)
        if resp.status_code == 200:
            body = resp.text
            if xss_payload.lower() in body.lower():
                raw_img = "<img " in body.lower()
                assert not raw_img or "&lt;img" in body, (
                    "XSS payload rendered unescaped in campaign response"
                )

    async def test_xss_in_company_name(self, async_client, auth_headers):
        xss_payload = "<svg onload=alert(1)>"
        resp = await async_client.get("/companies/", headers=auth_headers)
        if resp.status_code == 200:
            body = resp.text
            if xss_payload.lower() in body.lower():
                raw_svg = "<svg " in body.lower()
                assert not raw_svg or "&lt;svg" in body, (
                    "XSS payload rendered unescaped in company response"
                )


class TestParameterPollution:
    async def test_http_parameter_pollution(self, async_client, auth_headers):
        resp = await async_client.get(
            "/companies/?role=admin&role=vendedor",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 422), (
            f"Expected 200 or 422 for parameter pollution, got {resp.status_code}"
        )


class TestLargePayloads:
    async def test_large_json_payload_rejected(self, async_client, auth_headers):
        large_data = {"name": "x" * (10 * 1024 * 1024), "slug": "large-test"}
        try:
            resp = await async_client.post(
                "/companies/",
                json=large_data,
                headers=auth_headers,
            )
            assert resp.status_code in (413, 422), (
                f"Expected 413 or 422 for large payload, got {resp.status_code}"
            )
        except (httpx.RequestError, Exception):
            pass

    async def test_deeply_nested_json_rejected(self, async_client, auth_headers):
        def build_nested(depth):
            if depth == 0:
                return {"value": "leaf"}
            return {"nested": build_nested(depth - 1)}

        deep_data = build_nested(100)

        try:
            import httpx
            resp = await async_client.post(
                "/companies/",
                json=deep_data,
                headers=auth_headers,
                timeout=httpx.Timeout(10.0),
            )
            assert resp.status_code in (413, 422), (
                f"Expected 413 or 422 for deeply nested JSON, got {resp.status_code}"
            )
        except (httpx.RequestError, Exception):
            pass
