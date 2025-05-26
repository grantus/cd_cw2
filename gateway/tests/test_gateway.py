# gateway/tests/test_gateway.py

import io
import pytest
from fastapi.testclient import TestClient
from gateway.app import app

client = TestClient(app)

class DummyResponse:
    def __init__(self, status_code, json_data=None, content=b""):
        self.status_code = status_code
        self._json = json_data
        self.content = content
        self.text = content.decode("utf-8")

    def json(self):
        return self._json

@pytest.fixture(autouse=True)
def mock_services(monkeypatch):
    # Mock file_store & analysis endpoints
    async def fake_post(url, files=None):
        return DummyResponse(200, {"file_id": "abc"})
    async def fake_get(url):
        if "stats" in url:
            return DummyResponse(200, {"file_id": "abc", "words": 3})
        return DummyResponse(404, None)
    import httpx
    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    yield

def test_gateway_upload():
    # Emulate sending a file via gateway
    fileobj = io.BytesIO(b"foo")
    resp = client.post("/files/", files={"file": ("x.txt", fileobj, "text/plain")})
    assert resp.status_code == 200
    assert resp.json() == {"file_id": "abc"}

def test_gateway_stats_success():
    resp = client.get("/stats/abc")
    assert resp.status_code == 200
    assert resp.json()["words"] == 3

def test_gateway_stats_not_found():
    # fake_get returns 404 by default
    resp = client.get("/stats/404id")
    assert resp.status_code == 404
