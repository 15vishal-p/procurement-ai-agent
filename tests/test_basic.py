"""
Basic smoke tests. Deliberately avoid hitting Snowflake (no credentials
in CI) - these just confirm the app starts up correctly and the
expected routes are registered.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200


def test_expected_routes_registered():
    # Use FastAPI's own generated schema - reliable across versions,
    # unlike inspecting app.routes internals directly.
    schema = app.openapi()
    paths = set(schema["paths"].keys())
    assert "/contracts" in paths
    assert "/contracts/{contract_id}" in paths
    assert "/buyers/top" in paths
    assert "/stats/summary" in paths
