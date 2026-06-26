from unittest.mock import patch, MagicMock, call, ANY

import pytest

from app.services.email_service import send_privacy_request_notification


RESEND_API_URL = "https://api.resend.com/emails"
DPO_EMAIL = "privacidade@indiqr.lealcyber.com"


def _mock_resend_response(status_code=200, response_id="res-123"):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = {"id": response_id}
    mock_resp.raise_for_status = MagicMock()
    if status_code >= 400:
        mock_resp.raise_for_status.side_effect = Exception("HTTP error")
    return mock_resp


class TestPrivacyRequestNotification:
    def test_sends_to_dpo_email(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_privacy_request_notification(
                request_id=42,
                tipo="acesso",
                descricao="Gostaria de acessar todos os meus dados pessoais armazenados na plataforma.",
                email_contato="titular@example.com",
            )

        mock_post.assert_called_once()
        call_data = mock_post.call_args[1]["json"]
        assert call_data.get("to") == DPO_EMAIL

    def test_includes_request_details_in_html(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_privacy_request_notification(
                request_id=42,
                tipo="exclusao",
                descricao="Solicito a exclusão de todos os meus dados da plataforma IndiQR.",
                email_contato="titular@exemplo.com",
            )

        call_data = mock_post.call_args[1]["json"]
        html = call_data.get("html", "")
        assert "exclusao" in html.lower() or "Exclus" in html
        assert "titular@exemplo.com" in html

    def test_subject_contains_request_type(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_privacy_request_notification(
                request_id=1,
                tipo="portabilidade",
                descricao="Desejo exportar meus dados para portabilidade a outro serviço.",
                email_contato="user@test.com",
            )

        call_data = mock_post.call_args[1]["json"]
        subject = call_data.get("subject", "")
        assert "portabilidade" in subject.lower() or "Portabilidade" in subject

    def test_email_send_failure_graceful_degradation(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(500)

            result = send_privacy_request_notification(
                request_id=99,
                tipo="reclamacao",
                descricao="Reclamação sobre tratamento inadequado dos meus dados pessoais.",
                email_contato="reclamante@test.com",
            )

        assert result is False or result is None

    def test_network_error_does_not_crash(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.side_effect = ConnectionError("network down")

            try:
                send_privacy_request_notification(
                    request_id=1,
                    tipo="acesso",
                    descricao="Solicitação de acesso aos dados pessoais.",
                    email_contato="ok@test.com",
                )
            except Exception as e:
                pytest.fail(
                    f"send_privacy_request_notification raised unexpected {type(e).__name__}: {e}"
                )

    def test_timeout_does_not_crash(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.side_effect = TimeoutError("timed out")

            try:
                send_privacy_request_notification(
                    request_id=2,
                    tipo="correcao",
                    descricao="Meu email está incorreto no cadastro, preciso corrigir.",
                    email_contato="corrigir@test.com",
                )
            except Exception as e:
                pytest.fail(
                    f"send_privacy_request_notification raised unexpected {type(e).__name__}: {e}"
                )

    def test_renders_valid_html(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_privacy_request_notification(
                request_id=7,
                tipo="acesso",
                descricao="Solicitação de acesso aos dados pessoais conforme LGPD Art. 18.",
                email_contato="titular@test.com",
            )

        mock_post.assert_called_once()
        call_data = mock_post.call_args[1]["json"]
        html = call_data.get("html", "")
        assert isinstance(html, str)
        assert len(html) > 0
        assert (
            "<html" in html.lower()
            or "<!doctype" in html.lower()
            or "<body" in html.lower()
            or "<table" in html.lower()
        )

    def test_email_contato_nullable(self):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_privacy_request_notification(
                request_id=8,
                tipo="revogacao",
                descricao="Revogo meu consentimento para tratamento de dados pessoais.",
                email_contato=None,
            )

        mock_post.assert_called_once()
        call_data = mock_post.call_args[1]["json"]
        html = call_data.get("html", "")
        assert "não informado" in html.lower() or "sem email" in html.lower() or "anônimo" in html.lower()


PRIVACY_REQUEST_TYPES = [
    ("acesso", "Solicitação de Acesso"),
    ("correcao", "Solicitação de Correção"),
    ("exclusao", "Solicitação de Exclusão"),
    ("portabilidade", "Solicitação de Portabilidade"),
    ("revogacao", "Revogação de Consentimento"),
    ("reclamacao", "Reclamação"),
]


class TestPrivacyRequestTypeMapping:
    @pytest.mark.parametrize("tipo,expected_subject_label", PRIVACY_REQUEST_TYPES)
    def test_subject_reflects_tipo(self, tipo, expected_subject_label):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_privacy_request_notification(
                request_id=99,
                tipo=tipo,
                descricao=f"Teste de solicitação do tipo {tipo} com descrição suficiente.",
                email_contato="test@example.com",
            )

        call_data = mock_post.call_args[1]["json"]
        subject = call_data.get("subject", "")
        assert tipo in subject.lower()


class TestPrivacyRequestEmailRenderAllTypes:
    @pytest.mark.parametrize("tipo,_label", PRIVACY_REQUEST_TYPES)
    def test_all_tipos_render_valid_html(self, tipo, _label):
        with patch("app.services.email_service.requests.post") as mock_post:
            mock_post.return_value = _mock_resend_response(200)

            send_privacy_request_notification(
                request_id=1,
                tipo=tipo,
                descricao=f"Descrição de teste para o tipo {tipo} com mais de dez caracteres.",
                email_contato="titular@lgpd.com",
            )

        mock_post.assert_called_once()
        call_data = mock_post.call_args[1]["json"]
        html = call_data.get("html", "")
        assert isinstance(html, str)
        assert len(html) > 0
        assert (
            "<html" in html.lower()
            or "<!doctype" in html.lower()
            or "<body" in html.lower()
            or "<table" in html.lower()
        )
