import re
from unittest.mock import patch, MagicMock

import pytest

from app.services.qrcode_service import (
    generate_qrcode_image,
    generate_short_token,
    create_qrcode_for_campaign,
)


class TestGenerateQRCodeImage:
    def test_generate_qrcode_image_returns_bytes(self):
        data = "test-uuid-token"

        result = generate_qrcode_image(data)

        assert isinstance(result, bytes)

    def test_generate_qrcode_image_non_empty(self):
        data = "test-uuid-token"

        result = generate_qrcode_image(data)

        assert len(result) > 0

    def test_different_data_produces_different_images(self):
        result_a = generate_qrcode_image("token-a")
        result_b = generate_qrcode_image("token-b")

        assert result_a != result_b

    def test_empty_string_produces_valid_image(self):
        result = generate_qrcode_image("")

        assert isinstance(result, bytes)
        assert len(result) > 0


class TestGenerateShortToken:
    TOKEN_RE = re.compile(r"^[A-Za-z0-9]{6}$")

    def test_generate_short_token_length(self):
        token = generate_short_token()

        assert len(token) == 6

    def test_generate_short_token_alphanumeric(self):
        for _ in range(100):
            token = generate_short_token()
            assert self.TOKEN_RE.match(token), f"token={token!r} not alphanumeric"

    def test_generate_short_token_uniqueness(self):
        tokens = {generate_short_token() for _ in range(1000)}

        assert len(tokens) == 1000

    def test_charset_is_correct_size(self):
        token = generate_short_token()
        allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")

        assert set(token).issubset(allowed)


class TestCreateQRCodeForCampaign:
    def test_create_qrcode_for_campaign_active(self):
        campaign_id = 1
        influencer_id = 42

        with patch(
            "app.services.qrcode_service.uuid_module.uuid4"
        ) as mock_uuid, patch(
            "app.services.qrcode_service.generate_short_token"
        ) as mock_token:
            mock_uuid.return_value = "mock-uuid-1234"
            mock_token.return_value = "AbCd12"

            result = create_qrcode_for_campaign(campaign_id, influencer_id)

        assert result.get("campaign_id") == campaign_id
        assert result.get("influenciador_id") == influencer_id
        assert result.get("active") is True
        assert result.get("token") == "mock-uuid-1234"
        assert result.get("short_token") == "AbCd12"

    def test_create_qrcode_includes_unique_token(self):
        with patch(
            "app.services.qrcode_service.uuid_module.uuid4"
        ) as mock_uuid, patch(
            "app.services.qrcode_service.generate_short_token"
        ) as mock_token:
            mock_uuid.return_value = "uuid-a"
            mock_token.return_value = "Tok01"

            result_a = create_qrcode_for_campaign(1, 10)

            mock_uuid.return_value = "uuid-b"
            mock_token.return_value = "Tok02"

            result_b = create_qrcode_for_campaign(2, 20)

        assert result_a["token"] != result_b["token"]
        assert result_a["short_token"] != result_b["short_token"]

    def test_inactive_campaign_idempotent(self):
        """
        Creating a QRCode for an already-ended campaign should still succeed
        at the service level (caller handles active flag). The service
        does not enforce campaign status — it only creates the QRCode row.
        """
        with patch(
            "app.services.qrcode_service.uuid_module.uuid4"
        ) as mock_uuid, patch(
            "app.services.qrcode_service.generate_short_token"
        ) as mock_token:
            mock_uuid.return_value = "uuid-end"
            mock_token.return_value = "End99"

            result = create_qrcode_for_campaign(99, 7)

        assert result["active"] is True
        assert result["token"] is not None
        assert result["short_token"] is not None

    def test_image_generation_uses_token(self):
        campaign_id = 5
        influencer_id = 10

        with patch(
            "app.services.qrcode_service.uuid_module.uuid4"
        ) as mock_uuid, patch(
            "app.services.qrcode_service.generate_short_token"
        ) as mock_token:
            mock_uuid.return_value = "img-token-xyz"
            mock_token.return_value = "Zzz09"

            qrcode = create_qrcode_for_campaign(campaign_id, influencer_id)

        img = generate_qrcode_image(qrcode["token"])

        assert isinstance(img, bytes)
        assert len(img) > 0
