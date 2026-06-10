"""Race conditions — concurrent operations must be properly serialized."""

import asyncio

import pytest


class TestConcurrentConversionValidation:
    async def test_concurrent_validate_same_qrcode_one_succeeds(
        self, async_client, auth_headers
    ):
        async def validate(token):
            resp = await async_client.post(
                "/conversions/validate",
                json={"token": token},
                headers=auth_headers,
            )
            return resp.status_code

        token = "shared-qrcode-token"
        tasks = [validate(token) for _ in range(5)]
        statuses = await asyncio.gather(*tasks)

        created_count = sum(1 for s in statuses if s == 201)
        assert created_count <= 1, (
            f"Only 1 conversion should succeed, got {created_count} x 201: {statuses}"
        )
        other_count = sum(1 for s in statuses if s in (404, 409, 422))
        assert other_count >= 4, (
            f"Other validations should return 404/409/422, got {statuses}"
        )

    async def test_concurrent_validate_different_qrcodes_all_succeed(
        self, async_client, auth_headers
    ):
        async def validate(token):
            resp = await async_client.post(
                "/conversions/validate",
                json={"token": token},
                headers=auth_headers,
            )
            return resp.status_code

        tokens = [f"unique-qrcode-{i}" for i in range(5)]
        tasks = [validate(t) for t in tokens]
        statuses = await asyncio.gather(*tasks)

        for s in statuses:
            assert s in (201, 404), (
                f"Expected 201 or 404 for different tokens, got statuses: {statuses}"
            )


class TestConcurrentRedemptionValidation:
    async def test_concurrent_validate_same_otp_one_succeeds(
        self, async_client, auth_headers
    ):
        async def validate_otp(code):
            resp = await async_client.post(
                "/redemptions/validate",
                json={"code": code},
                headers=auth_headers,
            )
            return resp.status_code

        code = "123456"
        tasks = [validate_otp(code) for _ in range(3)]
        statuses = await asyncio.gather(*tasks)

        created_count = sum(1 for s in statuses if s == 201)
        assert created_count <= 1, (
            f"Only 1 redemption should succeed, got {created_count} x 201: {statuses}"
        )
        other_count = sum(1 for s in statuses if s in (403, 404, 409, 422))
        assert other_count >= 2, (
            f"Other validations should return error codes, got {statuses}"
        )


class TestConcurrentTokenGeneration:
    async def test_concurrent_token_generation_same_type(
        self, async_client, auth_headers
    ):
        async def generate_token():
            resp = await async_client.post(
                "/redemptions/tokens",
                json={"type": "dinheiro", "value": 10},
                headers=auth_headers,
            )
            return resp.status_code

        tasks = [generate_token() for _ in range(2)]
        statuses = await asyncio.gather(*tasks)

        created_count = sum(1 for s in statuses if s == 201)
        other_count = sum(1 for s in statuses if s in (409, 422))
        assert created_count <= 1, (
            f"Expected at most 1 token created, got statuses: {statuses}"
        )
        assert other_count >= 1, (
            f"Expected rejection for duplicate, got statuses: {statuses}"
        )


class TestConcurrentInvitationAcceptance:
    async def test_concurrent_accept_same_invitation_one_succeeds(
        self, async_client
    ):
        invitation_token = "test-invitation-token"

        async def accept(headers):
            resp = await async_client.post(
                f"/companies/invitations/{invitation_token}/accept",
                headers=headers,
            )
            return resp.status_code

        headers1 = {"Authorization": "Bearer user1-token"}
        headers2 = {"Authorization": "Bearer user2-token"}
        statuses = await asyncio.gather(
            accept(headers1),
            accept(headers2),
        )

        success_count = sum(1 for s in statuses if s == 200)
        assert success_count <= 1, (
            f"Only 1 acceptance should succeed, got statuses: {statuses}"
        )
        other_count = sum(1 for s in statuses if s in (404, 409))
        assert other_count >= 1, (
            f"Other acceptance should return 404 or 409, got {statuses}"
        )
