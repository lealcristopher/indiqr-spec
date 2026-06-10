from unittest.mock import patch, MagicMock, ANY

import pytest

from app.services.card_pdf_service import generate_card_pdf


SAMPLE_CAMPAIGN = {
    "id": 1,
    "name": "Campanha Verão 2026",
    "company_name": "Personalitte Biomedicina",
    "short_token": "XpW9k2",
    "qrcode_image": b"\x89PNG\r\n\x1a\nfake-png-bytes-for-test",
}


class TestGenerateCardPDF:
    def test_generate_card_pdf_returns_bytes(self):
        result = generate_card_pdf(
            campaign_name=SAMPLE_CAMPAIGN["name"],
            company_name=SAMPLE_CAMPAIGN["company_name"],
            short_token=SAMPLE_CAMPAIGN["short_token"],
            qrcode_image=SAMPLE_CAMPAIGN["qrcode_image"],
        )

        assert isinstance(result, bytes)

    def test_generate_card_pdf_valid_pdf_header(self):
        result = generate_card_pdf(
            campaign_name=SAMPLE_CAMPAIGN["name"],
            company_name=SAMPLE_CAMPAIGN["company_name"],
            short_token=SAMPLE_CAMPAIGN["short_token"],
            qrcode_image=SAMPLE_CAMPAIGN["qrcode_image"],
        )

        assert result[:4] == b"%PDF"

    def test_generate_card_pdf_contains_campaign_name(self):
        result = generate_card_pdf(
            campaign_name=SAMPLE_CAMPAIGN["name"],
            company_name=SAMPLE_CAMPAIGN["company_name"],
            short_token=SAMPLE_CAMPAIGN["short_token"],
            qrcode_image=SAMPLE_CAMPAIGN["qrcode_image"],
        )

        assert b"Campanha Ver\xc3\xa3o 2026" in result

    def test_generate_card_pdf_contains_short_token(self):
        result = generate_card_pdf(
            campaign_name=SAMPLE_CAMPAIGN["name"],
            company_name=SAMPLE_CAMPAIGN["company_name"],
            short_token=SAMPLE_CAMPAIGN["short_token"],
            qrcode_image=SAMPLE_CAMPAIGN["qrcode_image"],
        )

        assert b"XpW9k2" in result

    def test_generate_card_pdf_contains_company_name(self):
        result = generate_card_pdf(
            campaign_name=SAMPLE_CAMPAIGN["name"],
            company_name=SAMPLE_CAMPAIGN["company_name"],
            short_token=SAMPLE_CAMPAIGN["short_token"],
            qrcode_image=SAMPLE_CAMPAIGN["qrcode_image"],
        )

        assert b"Personalitte" in result

    def test_non_empty_pdf(self):
        result = generate_card_pdf(
            campaign_name=SAMPLE_CAMPAIGN["name"],
            company_name=SAMPLE_CAMPAIGN["company_name"],
            short_token=SAMPLE_CAMPAIGN["short_token"],
            qrcode_image=SAMPLE_CAMPAIGN["qrcode_image"],
        )

        assert len(result) > 4

    def test_different_inputs_produce_different_pdfs(self):
        pdf_a = generate_card_pdf(
            campaign_name="Campanha A",
            company_name="Empresa A",
            short_token="AAA111",
            qrcode_image=b"fake-a",
        )
        pdf_b = generate_card_pdf(
            campaign_name="Campanha B",
            company_name="Empresa B",
            short_token="BBB222",
            qrcode_image=b"fake-b",
        )

        assert pdf_a != pdf_b

    def test_handles_long_campaign_name(self):
        long_name = "Campanha " + "Muito " * 50 + "Longa"
        result = generate_card_pdf(
            campaign_name=long_name,
            company_name="TestCo",
            short_token="TesT01",
            qrcode_image=b"png-data",
        )

        assert isinstance(result, bytes)
        assert result[:4] == b"%PDF"

    def test_handles_special_characters(self):
        result = generate_card_pdf(
            campaign_name="Campanha & Cia. (Edição #1)",
            company_name="Empresa Ltda.",
            short_token="SpCh01",
            qrcode_image=b"png-data",
        )

        assert isinstance(result, bytes)
        assert result[:4] == b"%PDF"
