import io
import pytest
from flask import Flask, request, jsonify
import os, uuid

app = Flask(__name__)
UPLOAD_DIR = os.path.abspath(os.getenv("UPLOAD_DIR", "uploads"))

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f:
        return "no file provided", 400
    file_id = uuid.uuid4().hex
    save_path = os.path.join(UPLOAD_DIR, file_id)
    f.save(save_path)
    return jsonify({"file_id": file_id, "filename": f.filename})

@pytest.fixture()
def temp_upload_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("file_store.app.UPLOAD_DIR", str(tmp_path))
    os.makedirs(str(tmp_path), exist_ok=True)
    yield str(tmp_path)

def test_upload_file(temp_upload_dir):
    client = app.test_client()

    data = {
        "file": (io.BytesIO(b"test data"), "test.txt")
    }
    response = client.post("/upload", data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert "file_id" in response.json
