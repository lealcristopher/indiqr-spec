import logging
import re
from unittest.mock import patch, MagicMock

import pytest


OTP_REGEX = re.compile(r"\b\d{6}\b")
SHORT_TOKEN_REGEX = re.compile(r"^[A-Za-z0-9]{6}$")


class TestOTPLeakage:
    async def test_otp_code_masked_in_application_logs(self, caplog):
        caplog.set_level(logging.INFO)

        with patch("app.services.email_service.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"id": "res-123"}
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            from app.services.email_service import send_redemption_otp
            send_redemption_otp(
                influencer_email="inf@example.com",
                otp_code="921456",
            )

        log_text = caplog.text or ""
        for record in caplog.records:
            log_text += " " + record.getMessage()

        found = OTP_REGEX.findall(log_text)
        assert "921456" not in found, (
            f"OTP code '921456' found in plain text in logs: {found}"
        )

    async def test_otp_code_not_in_error_responses(self, async_client):
        resp = await async_client.post(
            "/redemptions/validate",
            json={"code": "999999"},
        )
        body = resp.json()
        assert resp.status_code == 404
        detail = body.get("detail", "")
        assert "999999" not in detail, (
            f"Error response echoed attempted OTP code: {detail}"
        )

    async def test_qrcode_token_not_in_error_responses(self, async_client):
        resp = await async_client.post(
            "/conversions/validate",
            json={"token": "invalid-qrcode-token-xyz"},
        )
        body = resp.json()
        assert "invalid-qrcode-token-xyz" not in str(body), (
            f"Error response echoed QRCode token: {body}"
        )


class TestShortTokenLeakage:
    async def test_campaign_short_token_not_leaked_in_url_logs(self, caplog):
        caplog.set_level(logging.INFO)
        from app.services.qrcode_service import generate_short_token
        short_token = generate_short_token()
        assert SHORT_TOKEN_REGEX.match(short_token)

        log_text = caplog.text or ""
        assert short_token not in log_text, (
            f"Short token {short_token!r} leaked in logs"
        )

    async def test_invitation_token_not_leaked(self, async_client):
        resp = await async_client.get(
            "/companies/invitations/preview/invalid-token-xyz"
        )
        body = resp.json()
        assert "invalid-token-xyz" not in str(body), (
            f"404 response echoed invitation token: {body}"
        )
