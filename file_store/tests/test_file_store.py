import io
import pytest

@pytest.fixture()
def temp_upload_dir(monkeypatch):
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdirname:
        monkeypatch.setenv("UPLOAD_DIR", tmpdirname)
        yield tmpdirname

@pytest.fixture
def client(temp_upload_dir):
    from file_store.app import app
    return app.test_client()

def test_upload_file(client):
    data = {
        "file": (io.BytesIO(b"test data"), "test.txt")
    }
    response = client.post("/upload", data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["filename"] == "test.txt"
    assert "file_id" in json_data
