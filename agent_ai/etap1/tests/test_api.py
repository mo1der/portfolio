def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_classify_rejects_empty_text(client):
    response = client.post(
        "/classify",
        json={"text": ""},
    )

    assert response.status_code == 422

    data = response.json()

    assert data["error"] == "ValidationError"
    assert data["message"] == "Invalid request data"
    assert data["details"][0]["field"] == "text"


def test_classify_rejects_blank_text(client):
    response = client.post(
        "/classify",
        json={"text": "     "},
    )

    assert response.status_code == 422

    data = response.json()

    assert data["error"] == "ValidationError"
    assert data["message"] == "Invalid request data"
    assert data["details"][0]["field"] == "text"