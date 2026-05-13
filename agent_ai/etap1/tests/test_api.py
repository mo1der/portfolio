from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "AI Classifier Backend działa"
    }


def test_classify_endpoint_finance():
    response = client.post(
        "/classify",
        json={
            "text": "Mam problem z fakturą za ostatni miesiąc."
        },
    )

    assert response.status_code == 200
    assert response.json()["category"] == "FINANCE"
    assert response.json()["priority"] == "HIGH"


def test_classify_endpoint_validation_error():
    response = client.post(
        "/classify",
        json={
            "wrong_field": "Brakuje pola text."
        },
    )

    assert response.status_code == 422

def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }