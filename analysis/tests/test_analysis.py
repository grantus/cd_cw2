import tempfile
import pytest
from gateway.app import app as gateway_app

@pytest.fixture
def client():
    return gateway_app.test_client()

@pytest.fixture()
def temp_upload_dir(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdirname:
        monkeypatch.setenv("UPLOAD_DIR", tmpdirname)
        yield tmpdirname



def test_analysis_workflow(client, temp_upload_dir):
    pass
