from unittest.mock import patch, MagicMock, call, ANY

import pytest

from app.services.email_service import (
    send_company_invite,
    send_campaign_invite,
    send_campaign_accepted,
    send_campaign_declined,
    send_campaign_ended,
    send_influencer_left_campaign,
    send_membership_request_notification,
    send_membership_accepted,
    send_membership_declined,
    send_conversion_notification,
    send_redemption_otp,
    send_shop_deployed,
)


RESEND_API_URL = "https://api.resend.com/emails"
VALID_HTML = "<!DOCTYPE html><html><body><p>Hello</p></body></html>"


def _mock_resend_response(status_code=200, response_id="res-123"):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = {"id": response_id}
    mock_resp.raise_for_status = MagicMock()
    if status_code >= 400:
        mock_resp.raise_for_status.side_effect = Exception("HTTP error")
    return mock_resp


class TestCompanyInvite:
    def test_send_company_invite_calls_resend_api(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_company_invite(
                to_email="invitee@example.com",
                company_name="Personalitte",
                role="influenciador",
                accept_url="https://indiqr.app/accept/abc",
            )

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == RESEND_API_URL

    def test_send_company_invite_includes_accept_url(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_company_invite(
                to_email="invitee@example.com",
                company_name="Personalitte",
                role="influenciador",
                accept_url="https://indiqr.app/accept/abc123",
            )

        call_data = mock_post.call_args[1]["json"]
        assert "https://indiqr.app/accept/abc123" in call_data.get("html", "")

    def test_send_company_invite_to_email_field(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_company_invite(
                to_email="target@example.com",
                company_name="TestCo",
                role="vendedor",
                accept_url="https://indiqr.app/accept/xyz",
            )

        call_data = mock_post.call_args[1]["json"]
        assert call_data.get("to") == "target@example.com"


class TestCampaignInvite:
    def test_send_campaign_invite_contains_accept_url(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_campaign_invite(
                to_email="influencer@example.com",
                campaign_name="Promoção Verão",
                company_name="Personalitte",
                accept_url="https://indiqr.app/campaign/1/accept",
                decline_url="https://indiqr.app/campaign/1/decline",
                remuneracao_desc="R$ 50,00 por conversão",
                desconto_desc=None,
            )

        call_data = mock_post.call_args[1]["json"]
        html = call_data.get("html", "")
        assert "https://indiqr.app/campaign/1/accept" in html

    def test_send_campaign_invite_contains_decline_url(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_campaign_invite(
                to_email="influencer@example.com",
                campaign_name="Promoção Verão",
                company_name="Personalitte",
                accept_url="https://indiqr.app/campaign/1/accept",
                decline_url="https://indiqr.app/campaign/1/decline",
                remuneracao_desc="R$ 50,00 por conversão",
                desconto_desc=None,
            )

        call_data = mock_post.call_args[1]["json"]
        html = call_data.get("html", "")
        assert "https://indiqr.app/campaign/1/decline" in html

    def test_send_campaign_invite_includes_remuneracao(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_campaign_invite(
                to_email="influencer@example.com",
                campaign_name="Promoção",
                company_name="TestCo",
                accept_url="https://x.com/a",
                decline_url="https://x.com/d",
                remuneracao_desc="10% do valor da venda",
                desconto_desc="5% de desconto para o cliente",
            )

        call_data = mock_post.call_args[1]["json"]
        html = call_data.get("html", "")
        assert "10%" in html
        assert "5%" in html

    def test_send_campaign_invite_subject_contains_campaign_name(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_campaign_invite(
                to_email="i@x.com",
                campaign_name="Super Promo",
                company_name="Co",
                accept_url="https://x.com/a",
                decline_url="https://x.com/d",
                remuneracao_desc="R$ 10",
                desconto_desc=None,
            )

        call_data = mock_post.call_args[1]["json"]
        subject = call_data.get("subject", "")
        assert "Super Promo" in subject


class TestEmailSendFailure:
    def test_email_send_failure_graceful_degradation(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(500)

            result = send_campaign_invite(
                to_email="fail@example.com",
                campaign_name="Test",
                company_name="Co",
                accept_url="https://x.com/a",
                decline_url="https://x.com/d",
                remuneracao_desc="R$ 10",
                desconto_desc=None,
            )

        assert result is False or result is None

    def test_network_error_does_not_crash(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.side_effect = ConnectionError("network down")

            try:
                send_company_invite(
                    to_email="fail@example.com",
                    company_name="TestCo",
                    role="influenciador",
                    accept_url="https://x.com/a",
                )
            except Exception as e:
                pytest.fail(f"send_company_invite raised unexpected {type(e).__name__}: {e}")

    def test_timeout_does_not_crash(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.side_effect = TimeoutError("timed out")

            try:
                send_campaign_accepted(
                    admin_email="admin@x.com",
                    influencer_email="inf@x.com",
                    campaign_name="Test",
                )
            except Exception as e:
                pytest.fail(f"send_campaign_accepted raised unexpected {type(e).__name__}: {e}")


EMAIL_TYPES = [
    ("send_company_invite", {
        "to_email": "inv@x.com", "company_name": "C", "role": "influenciador",
        "accept_url": "https://x.com/a",
    }),
    ("send_campaign_invite", {
        "to_email": "inf@x.com", "campaign_name": "Camp",
        "company_name": "Co", "accept_url": "https://x.com/a",
        "decline_url": "https://x.com/d", "remuneracao_desc": "R$ 10",
        "desconto_desc": None,
    }),
    ("send_campaign_accepted", {
        "admin_email": "adm@x.com", "influencer_email": "inf@x.com",
        "campaign_name": "Camp",
    }),
    ("send_campaign_declined", {
        "admin_email": "adm@x.com", "influencer_email": "inf@x.com",
        "campaign_name": "Camp",
    }),
    ("send_campaign_ended", {
        "influencer_email": "inf@x.com", "campaign_name": "Camp",
        "company_name": "Co",
    }),
    ("send_influencer_left_campaign", {
        "admin_email": "adm@x.com", "influencer_email": "inf@x.com",
        "campaign_name": "Camp",
    }),
    ("send_membership_request_notification", {
        "admin_email": "adm@x.com", "requester_email": "req@x.com",
        "company_name": "C", "role": "vendedor",
    }),
    ("send_membership_accepted", {
        "to_email": "req@x.com", "company_name": "C", "role": "vendedor",
    }),
    ("send_membership_declined", {
        "to_email": "req@x.com", "company_name": "C", "message": "No",
    }),
    ("send_conversion_notification", {
        "influencer_email": "inf@x.com", "campaign_name": "C",
        "valor_bruto": 100.0, "remuneracao_valor": 50.0,
    }),
    ("send_redemption_otp", {
        "influencer_email": "inf@x.com", "otp_code": "123456",
    }),
    ("send_shop_deployed", {
        "admin_email": "adm@x.com", "shop_name": "S", "shop_url": "https://s.com",
    }),
]


class TestAllEmailTypesRenderValidHTML:
    @pytest.mark.parametrize("func_name,kwargs", EMAIL_TYPES)
    def test_email_type_renders_valid_html(self, func_name, kwargs):
        email_module = __import__("app.services.email_service", fromlist=[func_name])
        send_func = getattr(email_module, func_name)

        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_func(**kwargs)

        mock_post.assert_called_once()
        call_data = mock_post.call_args[1]["json"]
        html = call_data.get("html", "")
        assert isinstance(html, str)
        assert len(html) > 0
        assert "<html" in html.lower() or "<!doctype" in html.lower() or "<body" in html.lower() or "<table" in html.lower()
