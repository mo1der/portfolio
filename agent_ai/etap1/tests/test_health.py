def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["app_name"] == "AI Classifier Backend"
    assert data["version"] == "1.5.0"
    assert data["environment"] == "test"
    assert data["ai_enabled"] is False