import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app import app
from config import Config

client = TestClient(app)

def test_path_traversal_protection():
    """Verify that path traversal attempts are blocked."""
    # Attempt to read a file outside the permitted directory
    # Using a relative path that tries to go up
    headers = {"X-API-KEY": Config.API_KEY}
    response = client.get("/api/read?path=../app.py", headers=headers)
    assert response.status_code == 403
    assert "Unauthorized access" in response.json()["detail"]

def test_api_key_protection():
    """Verify that endpoints are protected by API key."""
    response = client.get("/api/logs") # No header
    assert response.status_code == 403
    
    headers = {"X-API-KEY": "WRONG-KEY"}
    response = client.get("/api/logs", headers=headers)
    assert response.status_code == 403

def test_config_validation():
    """Verify config paths are initialized."""
    assert Path(Config.CHROMA_PERSIST_DIR).exists()
    assert Path(Config.DATA_DIR).exists()

def test_db_initialization():
    """Verify database file is created."""
    db_path = Path("nova_sentinel.db")
    assert db_path.exists()
