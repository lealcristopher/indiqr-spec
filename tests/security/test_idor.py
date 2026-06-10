"""IDOR — Insecure Direct Object Reference tests.

Cross-company access control and enumeration resistance.
Users from company A must not access resources belonging to company B.
"""

import pytest


class TestCrossCompanyAccess:
    @pytest.fixture(autouse=True)
    async def setup_companies(self, async_client, valid_token_admin):
        admin_headers = {"Authorization": f"Bearer {valid_token_admin}"}
        resp = await async_client.post(
            "/companies/",
            json={"name": "Company A IDOR Test", "slug": "company-a-idor"},
            headers=admin_headers,
        )
        self.company_a = resp.json() if resp.status_code == 201 else {"id": 1}

        resp = await async_client.post(
            "/companies/",
            json={"name": "Company B IDOR Test", "slug": "company-b-idor"},
            headers=admin_headers,
        )
        self.company_b = resp.json() if resp.status_code == 201 else {"id": 2}

    async def test_cannot_access_other_company_members(
        self, async_client, valid_token_vendedor
    ):
        headers = {"Authorization": f"Bearer {valid_token_vendedor}"}
        resp = await async_client.get(
            f"/companies/{self.company_b['id']}/members",
            headers=headers,
        )
        assert resp.status_code in (403, 404), (
            f"Expected 403 or 404, got {resp.status_code}"
        )

    async def test_cannot_access_other_company_invitations(
        self, async_client, valid_token_vendedor
    ):
        headers = {"Authorization": f"Bearer {valid_token_vendedor}"}
        resp = await async_client.get(
            f"/companies/{self.company_b['id']}/invitations",
            headers=headers,
        )
        assert resp.status_code in (403, 404), (
            f"Expected 403 or 404, got {resp.status_code}"
        )

    async def test_cannot_access_other_campaign(
        self, async_client, valid_token_influenciador
    ):
        headers = {"Authorization": f"Bearer {valid_token_influenciador}"}
        resp = await async_client.get("/campaigns/999999", headers=headers)
        assert resp.status_code in (403, 404), (
            f"Expected 403 or 404, got {resp.status_code}"
        )

    async def test_cannot_access_other_conversion(
        self, async_client, valid_token_vendedor
    ):
        headers = {"Authorization": f"Bearer {valid_token_vendedor}"}
        resp = await async_client.get(
            f"/campaigns/{self.company_b['id']}/conversions",
            headers=headers,
        )
        assert resp.status_code in (403, 404), (
            f"Expected 403 or 404, got {resp.status_code}"
        )

    async def test_cannot_validate_redemption_other_company(
        self, async_client, valid_token_vendedor
    ):
        headers = {"Authorization": f"Bearer {valid_token_vendedor}"}
        resp = await async_client.post(
            "/redemptions/validate",
            json={"code": "000000"},
            headers=headers,
        )
        assert resp.status_code in (403, 404, 422), (
            f"Cross-company redemption validate returned {resp.status_code}"
        )

    async def test_cannot_delete_other_redemption_token(
        self, async_client, valid_token_influenciador
    ):
        headers = {"Authorization": f"Bearer {valid_token_influenciador}"}
        resp = await async_client.delete(
            "/redemptions/tokens/999999",
            headers=headers,
        )
        assert resp.status_code in (403, 404), (
            f"Expected 403 or 404, got {resp.status_code}"
        )

    async def test_cannot_cancel_other_invitation(
        self, async_client, valid_token_admin
    ):
        headers = {"Authorization": f"Bearer {valid_token_admin}"}
        resp = await async_client.delete(
            f"/companies/{self.company_a['id']}/invitations/999999",
            headers=headers,
        )
        assert resp.status_code == 404, (
            f"Expected 404 (not revealing existence), got {resp.status_code}"
        )


class TestEnumerationResistance:
    async def test_member_list_no_enumeration(
        self, async_client, valid_token_vendedor
    ):
        headers = {"Authorization": f"Bearer {valid_token_vendedor}"}
        resp = await async_client.get(
            "/companies/99999/members",
            headers=headers,
        )
        assert resp.status_code == 403, (
            f"Expected 403 for non-member access, got {resp.status_code}"
        )

    async def test_campaign_no_enumeration(
        self, async_client, valid_token_influenciador
    ):
        headers = {"Authorization": f"Bearer {valid_token_influenciador}"}
        resp = await async_client.get("/campaigns/99999", headers=headers)
        assert resp.status_code == 403, (
            f"Expected 403 for cross-company campaign, got {resp.status_code}"
        )

    async def test_conversion_no_enumeration(
        self, async_client, valid_token_vendedor
    ):
        headers = {"Authorization": f"Bearer {valid_token_vendedor}"}
        resp = await async_client.get(
            "/conversions/?campaign_id=99999",
            headers=headers,
        )
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("data", data.get("items", []))
            assert len(items) == 0, (
                "Conversions list should be empty, not 403"
            )

    async def test_invitation_no_enumeration(
        self, async_client, valid_token_admin
    ):
        headers = {"Authorization": f"Bearer {valid_token_admin}"}
        resp = await async_client.get(
            "/companies/99999/invitations",
            headers=headers,
        )
        assert resp.status_code == 404, (
            f"Expected 404 for nonexistent company invitations, got {resp.status_code}"
        )

    async def test_redemption_token_no_enumeration(
        self, async_client, valid_token_influenciador
    ):
        headers = {"Authorization": f"Bearer {valid_token_influenciador}"}
        resp = await async_client.delete(
            "/redemptions/tokens/99999",
            headers=headers,
        )
        assert resp.status_code in (403, 404), (
            f"Expected 403 or 404, got {resp.status_code}"
        )
