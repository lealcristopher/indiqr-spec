import pytest


@pytest.fixture
def mock_db_session():
    from unittest.mock import MagicMock

    session = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.add = MagicMock()
    session.refresh = MagicMock(side_effect=lambda obj: obj)
    return session
