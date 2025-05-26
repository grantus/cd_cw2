import pytest

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("FILE_STORE_URL", "http://localhost:5000")
    monkeypatch.setenv("ANALYSIS_URL", "http://localhost:5001")

@pytest.fixture
def client():
    from gateway.app import app
    return app.test_client()

def test_gateway_functionality(client):
    pass
