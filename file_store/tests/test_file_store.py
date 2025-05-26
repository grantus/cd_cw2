import os
import io
import uuid
import pytest
from fastapi.testclient import TestClient
from file_store.app import app, UPLOAD_DIR

client = TestClient(app)

def test_upload_txt(tmp_path, monkeypatch):
    # Prepare a small text file
    sample = tmp_path / "hello.txt"
    sample.write_text("Hello\nWorld")
    with open(sample, "rb") as f:
        response = client.post(
            "/files/",
            files={"file": ("hello.txt", f, "text/plain")}
        )
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    # file_id is a UUID string
    uuid.UUID(data["file_id"])
    # file exists on disk
    path = os.path.join(UPLOAD_DIR, f"{data['file_id']}.txt")
    assert os.path.isfile(path)

def test_upload_non_txt():
    # Try uploading a .png → should 400
    fake = io.BytesIO(b"\x89PNG\r\n")
    response = client.post(
        "/files/",
        files={"file": ("image.png", fake, "image/png")}
    )
    assert response.status_code == 400
    assert "Only .txt allowed" in response.text

def test_overwrite_same_id(monkeypatch):
    # Force a fixed UUID so second upload would overwrite
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    def fake_uuid4():
        import uuid as _u; return _u.UUID(fake_id)
    monkeypatch.setattr("app.uuid.uuid4", fake_uuid4)

    # First upload
    response1 = client.post(
        "/files/",
        files={"file": ("a.txt", io.BytesIO(b"x"), "text/plain")}
    )
    assert response1.json()["file_id"] == fake_id
    # Second upload with same fake_id
    response2 = client.post(
        "/files/",
        files={"file": ("b.txt", io.BytesIO(b"y"), "text/plain")}
    )
    assert response2.json()["file_id"] == fake_id
    # Content on disk should be last upload
    path = os.path.join(UPLOAD_DIR, fake_id + ".txt")
    assert open(path, "rb").read() == b"y"
