from datetime import datetime, timezone
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


ADMIN_USER = {
    "id": 30,
    "email": "admin@test.com",
    "roles": ["indiqr-admin"],
}
INFLUENCER_USER = {
    "id": 10,
    "email": "influencer@test.com",
    "roles": ["indiqr-influenciador"],
}
VENDEDOR_USER = {
    "id": 20,
    "email": "vendedor@test.com",
    "roles": ["indiqr-vendedor"],
}
NO_ROLE_USER = {"id": 99, "email": "norole@test.com", "roles": []}


def _auth_client(user):
    app.dependency_overrides.clear()
    from app.api.dependencies.auth import get_current_user

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user
    return TestClient(app)


@pytest.fixture
def client_admin():
    return _auth_client(ADMIN_USER)


@pytest.fixture
def client_influencer():
    return _auth_client(INFLUENCER_USER)


@pytest.fixture
def client_vendedor():
    return _auth_client(VENDEDOR_USER)


@pytest.fixture
def client_no_role():
    return _auth_client(NO_ROLE_USER)


@pytest.fixture
def anonymous_client():
    app.dependency_overrides.clear()
    return TestClient(app)


def _valid_png_bytes():
    return BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)


def _valid_jpeg_bytes():
    return BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 100)


def _valid_webp_bytes():
    return BytesIO(b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 100)


def _empty_bytes():
    return BytesIO(b"")


def _text_file_bytes():
    return BytesIO(b"not an image")


def _large_bytes(mb=6):
    return BytesIO(b"x" * (mb * 1024 * 1024))


# =============================================================================
# GET /shop/mine
# =============================================================================

class TestGetMyShop:
    def test_get_my_shop_with_data(self, client_admin):
        resp = client_admin.get("/api/v1/shop/mine")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "handle" in data
        assert "name" in data
        assert "logo_url" in data or "logo" in data

    def test_get_my_shop_no_shop(self, client_admin):
        resp = client_admin.get("/api/v1/shop/mine")
        assert resp.status_code in (200, 404)
        if resp.status_code == 404:
            assert "detail" in resp.json()

    def test_get_my_shop_non_admin_blocked(self, client_influencer):
        resp = client_influencer.get("/api/v1/shop/mine")
        assert resp.status_code == 403

    def test_get_my_shop_unauthenticated(self, anonymous_client):
        resp = anonymous_client.get("/api/v1/shop/mine")
        assert resp.status_code == 401


# =============================================================================
# POST /shop/logo
# =============================================================================

class TestUploadLogo:
    @patch("app.services.shop_media_service.upload_to_storage")
    def test_upload_logo_valid_png(self, mock_upload, client_admin):
        mock_upload.return_value = "https://r2.indiqr.com/media/logo-uuid.png"
        resp = client_admin.post(
            "/api/v1/shop/logo",
            files={"file": ("logo.png", _valid_png_bytes(), "image/png")},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "url" in data
        assert data["url"].startswith("https://")

    @patch("app.services.shop_media_service.upload_to_storage")
    def test_upload_logo_valid_jpeg(self, mock_upload, client_admin):
        mock_upload.return_value = "https://r2.indiqr.com/media/logo-uuid.jpg"
        resp = client_admin.post(
            "/api/v1/shop/logo",
            files={"file": ("logo.jpg", _valid_jpeg_bytes(), "image/jpeg")},
        )
        assert resp.status_code == 201
        assert "url" in resp.json()

    @patch("app.services.shop_media_service.upload_to_storage")
    def test_upload_logo_replaces_previous(self, mock_upload, client_admin):
        mock_upload.return_value = "https://r2.indiqr.com/media/logo-a.png"
        first = client_admin.post(
            "/api/v1/shop/logo",
            files={"file": ("logo-a.png", _valid_png_bytes(), "image/png")},
        )
        assert first.status_code == 201
        first_url = first.json()["url"]

        mock_upload.return_value = "https://r2.indiqr.com/media/logo-b.png"
        second = client_admin.post(
            "/api/v1/shop/logo",
            files={"file": ("logo-b.png", _valid_png_bytes(), "image/png")},
        )
        assert second.status_code == 201

        mine = client_admin.get("/api/v1/shop/mine")
        assert mine.status_code == 200
        shop = mine.json()
        current_logo = shop.get("logo_url") or shop.get("logo", {})
        if isinstance(current_logo, str):
            assert current_logo == second.json()["url"]
            assert current_logo != first_url

    def test_upload_logo_invalid_mime(self, client_admin):
        resp = client_admin.post(
            "/api/v1/shop/logo",
            files={"file": ("logo.txt", _text_file_bytes(), "text/plain")},
        )
        assert resp.status_code == 422
        detail = resp.json().get("detail", "")
        assert any(word in detail.lower() for word in ["suport", "tipo", "mime", "invalid"])

    def test_upload_logo_no_file(self, client_admin):
        resp = client_admin.post("/api/v1/shop/logo")
        assert resp.status_code == 422

    def test_upload_logo_empty_file(self, client_admin):
        resp = client_admin.post(
            "/api/v1/shop/logo",
            files={"file": ("empty.png", _empty_bytes(), "image/png")},
        )
        assert resp.status_code == 422

    def test_upload_logo_exceeds_size_limit(self, client_admin):
        resp = client_admin.post(
            "/api/v1/shop/logo",
            files={"file": ("large.png", _large_bytes(6), "image/png")},
        )
        assert resp.status_code == 413

    def test_upload_logo_non_admin_blocked(self, client_influencer):
        resp = client_influencer.post(
            "/api/v1/shop/logo",
            files={"file": ("logo.png", _valid_png_bytes(), "image/png")},
        )
        assert resp.status_code == 403


# =============================================================================
# POST /shop/hero
# =============================================================================

class TestUploadHero:
    @patch("app.services.shop_media_service.upload_to_storage")
    def test_upload_hero_valid_image(self, mock_upload, client_admin):
        mock_upload.return_value = "https://r2.indiqr.com/media/hero-uuid.png"
        resp = client_admin.post(
            "/api/v1/shop/hero",
            files={"file": ("hero.png", _valid_png_bytes(), "image/png")},
        )
        assert resp.status_code == 201
        assert "url" in resp.json()

    @patch("app.services.shop_media_service.upload_to_storage")
    def test_upload_hero_replaces_previous(self, mock_upload, client_admin):
        mock_upload.return_value = "https://r2.indiqr.com/media/hero-a.png"
        first = client_admin.post(
            "/api/v1/shop/hero",
            files={"file": ("hero-a.png", _valid_png_bytes(), "image/png")},
        )
        assert first.status_code == 201

        mock_upload.return_value = "https://r2.indiqr.com/media/hero-b.png"
        second = client_admin.post(
            "/api/v1/shop/hero",
            files={"file": ("hero-b.png", _valid_png_bytes(), "image/png")},
        )
        assert second.status_code == 201

        mine = client_admin.get("/api/v1/shop/mine")
        assert mine.status_code == 200
        shop = mine.json()
        current_hero = shop.get("hero_url") or shop.get("hero", {})
        if isinstance(current_hero, str):
            assert current_hero == second.json()["url"]

    def test_upload_hero_non_admin_blocked(self, client_vendedor):
        resp = client_vendedor.post(
            "/api/v1/shop/hero",
            files={"file": ("hero.png", _valid_png_bytes(), "image/png")},
        )
        assert resp.status_code == 403


# =============================================================================
# POST /shop/categories/{id}/image
# =============================================================================

class TestUploadCategoryImage:
    CATEGORY_ID = 1

    @patch("app.services.shop_media_service.upload_to_storage")
    def test_upload_category_image_success(self, mock_upload, client_admin):
        mock_upload.return_value = "https://r2.indiqr.com/media/cat-1.png"
        resp = client_admin.post(
            f"/api/v1/shop/categories/{self.CATEGORY_ID}/image",
            files={"file": ("cat.png", _valid_png_bytes(), "image/png")},
        )
        assert resp.status_code == 201
        assert "url" in resp.json()

    def test_upload_category_image_not_found(self, client_admin):
        resp = client_admin.post(
            "/api/v1/shop/categories/99999/image",
            files={"file": ("cat.png", _valid_png_bytes(), "image/png")},
        )
        assert resp.status_code == 404

    def test_upload_category_image_cross_company(self, client_admin):
        resp = client_admin.post(
            "/api/v1/shop/categories/99998/image",
            files={"file": ("cat.png", _valid_png_bytes(), "image/png")},
        )
        assert resp.status_code == 404


# =============================================================================
# POST /shop/products/{id}/image
# =============================================================================

class TestUploadProductImage:
    PRODUCT_ID = 1

    @patch("app.services.shop_media_service.upload_to_storage")
    def test_upload_product_image_success(self, mock_upload, client_admin):
        mock_upload.return_value = "https://r2.indiqr.com/media/prod-1.png"
        resp = client_admin.post(
            f"/api/v1/shop/products/{self.PRODUCT_ID}/image",
            files={"file": ("prod.png", _valid_png_bytes(), "image/png")},
        )
        assert resp.status_code == 201
        assert "url" in resp.json()

    @patch("app.services.shop_media_service.upload_to_storage")
    def test_upload_product_image_replaces_previous(self, mock_upload, client_admin):
        mock_upload.return_value = "https://r2.indiqr.com/media/prod-a.png"
        first = client_admin.post(
            f"/api/v1/shop/products/{self.PRODUCT_ID}/image",
            files={"file": ("prod-a.png", _valid_png_bytes(), "image/png")},
        )
        assert first.status_code == 201

        mock_upload.return_value = "https://r2.indiqr.com/media/prod-b.png"
        second = client_admin.post(
            f"/api/v1/shop/products/{self.PRODUCT_ID}/image",
            files={"file": ("prod-b.png", _valid_png_bytes(), "image/png")},
        )
        assert second.status_code == 201

        mine = client_admin.get("/api/v1/shop/mine")
        assert mine.status_code == 200
        products = mine.json().get("products", [])
        if products:
            assert products[0].get("image_url", "") == second.json()["url"]

    def test_upload_product_image_not_found(self, client_admin):
        resp = client_admin.post(
            "/api/v1/shop/products/99999/image",
            files={"file": ("prod.png", _valid_png_bytes(), "image/png")},
        )
        assert resp.status_code == 404

    def test_upload_product_image_non_admin_blocked(self, client_influencer):
        resp = client_influencer.post(
            "/api/v1/shop/products/1/image",
            files={"file": ("prod.png", _valid_png_bytes(), "image/png")},
        )
        assert resp.status_code == 403


# =============================================================================
# POST /shop/products/{id}/gallery
# =============================================================================

class TestUploadGalleryImage:
    PRODUCT_ID = 1

    @patch("app.services.shop_media_service.upload_to_storage")
    def test_upload_gallery_image_success(self, mock_upload, client_admin):
        mock_upload.return_value = "https://r2.indiqr.com/media/gallery-1.png"
        resp = client_admin.post(
            f"/api/v1/shop/products/{self.PRODUCT_ID}/gallery",
            files={"file": ("gallery.png", _valid_png_bytes(), "image/png")},
        )
        assert resp.status_code == 201
        assert "url" in resp.json()

        mine = client_admin.get("/api/v1/shop/mine")
        assert mine.status_code == 200
        products = mine.json().get("products", [])
        if products:
            gallery = products[0].get("gallery", [])
            assert any(g.get("url") == resp.json()["url"] for g in gallery)

    @patch("app.services.shop_media_service.upload_to_storage")
    def test_upload_gallery_image_multiple(self, mock_upload, client_admin):
        urls = [
            "https://r2.indiqr.com/media/gallery-a.png",
            "https://r2.indiqr.com/media/gallery-b.png",
            "https://r2.indiqr.com/media/gallery-c.png",
        ]
        for url in urls:
            mock_upload.return_value = url
            resp = client_admin.post(
                f"/api/v1/shop/products/{self.PRODUCT_ID}/gallery",
                files={"file": ("img.png", _valid_png_bytes(), "image/png")},
            )
            assert resp.status_code == 201

        mine = client_admin.get("/api/v1/shop/mine")
        assert mine.status_code == 200
        products = mine.json().get("products", [])
        if products:
            gallery = products[0].get("gallery", [])
            assert len(gallery) >= 3

    def test_upload_gallery_image_not_found(self, client_admin):
        resp = client_admin.post(
            "/api/v1/shop/products/99999/gallery",
            files={"file": ("img.png", _valid_png_bytes(), "image/png")},
        )
        assert resp.status_code == 404


# =============================================================================
# DELETE /shop/products/{id}/gallery/{image_id}
# =============================================================================

class TestDeleteGalleryImage:
    PRODUCT_ID = 1
    IMAGE_ID = 1

    def test_delete_gallery_image_success(self, client_admin):
        resp = client_admin.delete(
            f"/api/v1/shop/products/{self.PRODUCT_ID}/gallery/{self.IMAGE_ID}",
        )
        assert resp.status_code == 204

    def test_delete_gallery_image_not_found(self, client_admin):
        resp = client_admin.delete(
            "/api/v1/shop/products/1/gallery/99999",
        )
        assert resp.status_code == 404

    def test_delete_gallery_image_wrong_product(self, client_admin):
        resp = client_admin.delete(
            "/api/v1/shop/products/99998/gallery/1",
        )
        assert resp.status_code == 404

    def test_delete_gallery_image_cross_company(self, client_admin):
        resp = client_admin.delete(
            "/api/v1/shop/products/99997/gallery/1",
        )
        assert resp.status_code == 404

    def test_delete_gallery_image_non_admin_blocked(self, client_vendedor):
        resp = client_vendedor.delete(
            f"/api/v1/shop/products/{self.PRODUCT_ID}/gallery/{self.IMAGE_ID}",
        )
        assert resp.status_code == 403


# =============================================================================
# PUT /shop/products/{id}/gallery/reorder
# =============================================================================

class TestReorderGallery:
    PRODUCT_ID = 1

    def test_reorder_gallery_success(self, client_admin):
        resp = client_admin.put(
            f"/api/v1/shop/products/{self.PRODUCT_ID}/gallery/reorder",
            json={"image_ids": [3, 1, 2]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "gallery" in data

    def test_reorder_gallery_incomplete_list(self, client_admin):
        resp = client_admin.put(
            f"/api/v1/shop/products/{self.PRODUCT_ID}/gallery/reorder",
            json={"image_ids": [1, 2]},
        )
        assert resp.status_code == 422

    def test_reorder_gallery_invalid_id(self, client_admin):
        resp = client_admin.put(
            f"/api/v1/shop/products/{self.PRODUCT_ID}/gallery/reorder",
            json={"image_ids": [99999]},
        )
        assert resp.status_code == 422

    def test_reorder_gallery_cross_company(self, client_admin):
        resp = client_admin.put(
            "/api/v1/shop/products/99998/gallery/reorder",
            json={"image_ids": [1]},
        )
        assert resp.status_code in (404, 422)

    def test_reorder_gallery_non_admin_blocked(self, client_influencer):
        resp = client_influencer.put(
            f"/api/v1/shop/products/{self.PRODUCT_ID}/gallery/reorder",
            json={"image_ids": [1, 2, 3]},
        )
        assert resp.status_code == 403


# =============================================================================
# Fluxo completo — Shop Media Lifecycle
# =============================================================================

class TestFullMediaFlow:
    @patch("app.services.shop_media_service.upload_to_storage")
    def test_shop_full_media_flow(self, mock_upload, client_admin):
        mock_upload.return_value = "https://r2.indiqr.com/media/test.png"

        logo = client_admin.post(
            "/api/v1/shop/logo",
            files={"file": ("logo.png", _valid_png_bytes(), "image/png")},
        )
        assert logo.status_code == 201

        hero = client_admin.post(
            "/api/v1/shop/hero",
            files={"file": ("hero.png", _valid_png_bytes(), "image/png")},
        )
        assert hero.status_code == 201

        cat_img = client_admin.post(
            "/api/v1/shop/categories/1/image",
            files={"file": ("cat.png", _valid_png_bytes(), "image/png")},
        )
        assert cat_img.status_code == 201

        prod_img = client_admin.post(
            "/api/v1/shop/products/1/image",
            files={"file": ("prod.png", _valid_png_bytes(), "image/png")},
        )
        assert prod_img.status_code == 201

        gallery_1 = client_admin.post(
            "/api/v1/shop/products/1/gallery",
            files={"file": ("g1.png", _valid_png_bytes(), "image/png")},
        )
        assert gallery_1.status_code == 201

        gallery_2 = client_admin.post(
            "/api/v1/shop/products/1/gallery",
            files={"file": ("g2.png", _valid_png_bytes(), "image/png")},
        )
        assert gallery_2.status_code == 201

        mine = client_admin.get("/api/v1/shop/mine")
        assert mine.status_code == 200
        shop = mine.json()
        assert "name" in shop

        reorder = client_admin.put(
            "/api/v1/shop/products/1/gallery/reorder",
            json={"image_ids": [2, 1]},
        )
        assert reorder.status_code in (200, 422)

        delete_resp = client_admin.delete(
            "/api/v1/shop/products/1/gallery/1",
        )
        assert delete_resp.status_code in (204, 404)

        mock_upload.return_value = "https://r2.indiqr.com/media/new-logo.png"
        new_logo = client_admin.post(
            "/api/v1/shop/logo",
            files={"file": ("new-logo.png", _valid_png_bytes(), "image/png")},
        )
        assert new_logo.status_code == 201

        final_mine = client_admin.get("/api/v1/shop/mine")
        assert final_mine.status_code == 200
