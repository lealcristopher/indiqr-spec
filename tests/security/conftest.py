import os
import time
from unittest.mock import MagicMock, patch

import pytest
import httpx
from jose import jwt as jose_jwt

API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "indiqr-dev.us.auth0.com")
AUDIENCE = os.environ.get("AUDIENCE", "https://indiqr-api.lealcyber.com")
ISSUER = os.environ.get("ISSUER", f"https://{AUTH0_DOMAIN}/")
LOCAL_JWKS_SECRET = os.environ.get("LOCAL_JWKS_SECRET", "test-secret-key-for-local-jwks-32chars!")
LOCAL_JWKS_ALGORITHM = "HS256"

ROLE_CLAIM = "https://indiqr.lealcyber.com/roles"


def _make_jwt(
    sub="auth0|test-user",
    roles=None,
    exp=None,
    aud=AUDIENCE,
    iss=ISSUER,
    iat=None,
    secret=LOCAL_JWKS_SECRET,
    algorithm=LOCAL_JWKS_ALGORITHM,
):
    if roles is None:
        roles = ["admin"]
    if iat is None:
        iat = int(time.time())
    if exp is None:
        exp = iat + 3600

    payload = {
        "sub": sub,
        "iss": iss,
        "aud": aud,
        "iat": iat,
        "exp": exp,
        "azp": "test-client-id",
        "scope": "openid profile email",
        ROLE_CLAIM: roles,
    }
    return jose_jwt.encode(payload, secret, algorithm=algorithm)


@pytest.fixture
def api_base():
    return API_BASE


@pytest.fixture
def audience():
    return AUDIENCE


@pytest.fixture
def issuer():
    return ISSUER


@pytest.fixture
def local_jwks_secret():
    return LOCAL_JWKS_SECRET


@pytest.fixture
def valid_token(local_jwks_secret):
    return _make_jwt(secret=local_jwks_secret)


@pytest.fixture
def valid_token_admin(local_jwks_secret):
    return _make_jwt(roles=["admin"], secret=local_jwks_secret)


@pytest.fixture
def valid_token_vendedor(local_jwks_secret):
    return _make_jwt(roles=["vendedor"], secret=local_jwks_secret)


@pytest.fixture
def valid_token_influenciador(local_jwks_secret):
    return _make_jwt(roles=["influenciador"], secret=local_jwks_secret)


@pytest.fixture
def auth_headers(valid_token):
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
def async_client(api_base):
    client = httpx.AsyncClient(base_url=api_base)
    yield client


@pytest.fixture
def make_jwt():
    return _make_jwt


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.add = MagicMock()
    session.refresh = MagicMock(side_effect=lambda obj: obj)
    session.execute = MagicMock()
    session.query = MagicMock()
    return session
