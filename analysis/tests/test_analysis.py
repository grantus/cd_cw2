# analysis/tests/test_analysis.py

import os
import sqlite3
import pytest
from fastapi.testclient import TestClient
from analysis.app import app, UPLOAD_DIR

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db(tmp_path, monkeypatch):
    # Point SQLite to temporary file
    db_path = tmp_path / "stats.db"
    monkeypatch.setenv("STATS_DB", str(db_path))
    # Ensure uploads dir points to a tmp uploads
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setenv("UPLOAD_DIR", str(uploads))
    # Reimport app globals
    import importlib
    importlib.reload(__import__("app"))
    yield
    # teardown automatically

def create_txt(tmp_path, file_id, content):
    # helper to write test file
    uploads = os.environ["UPLOAD_DIR"]
    path = os.path.join(uploads, f"{file_id}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_id

def test_missing_file():
    res = client.get("/stats/not-there")
    assert res.status_code == 404

def test_compute_and_cache(monkeypatch, tmp_path):
    # write a file with 2 paragraphs, 5 words, 20 chars
    fid = create_txt(tmp_path, "f1", "one two\n\nthree four five")
    # First call: computes
    r1 = client.get(f"/stats/{fid}")
    assert r1.status_code == 200
    js = r1.json()
    assert js["paragraphs"] == 2
    assert js["words"] == 5
    assert js["chars"] == len("one two\n\nthree four five")
    # Now manually corrupt file to ensure caching works
    path = os.path.join(os.environ["UPLOAD_DIR"], f"{fid}.txt")
    with open(path, "w") as f:
        f.write("bad data")
    # Second call: still returns old stats
    r2 = client.get(f"/stats/{fid}")
    js2 = r2.json()
    assert js2 == js

def test_db_persistent(tmp_path, monkeypatch):
    # Check SQLite file is created
    db_file = tmp_path / "stats.db"
    monkeypatch.setenv("STATS_DB", str(db_file))
    import importlib; importlib.reload(__import__("app"))
    # No stats yet, DB empty
    conn = sqlite3.connect(str(db_file))
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stats'")
    assert cur.fetchone() is not None
