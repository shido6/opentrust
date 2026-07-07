import pytest


@pytest.fixture
def api_key():
    return "test-key"


@pytest.fixture
def auth_headers(api_key):
    return {"X-API-Key": api_key}
