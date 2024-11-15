from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/api/dummy/health-check")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}
