from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_dashboard_tickets_by_day_empty_database():
    response = client.get("/dashboard/tickets-by-day")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert data["items"] == []


def test_dashboard_tickets_by_day_after_process():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "API",
        },
    )

    assert process_response.status_code == 200

    response = client.get("/dashboard/tickets-by-day")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["count"] == 1
    assert "date" in data["items"][0]


def test_dashboard_tickets_by_day_counts_multiple_tickets_same_day():
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "API",
        },
    )

    client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem.",
            "source_channel": "API",
        },
    )

    client.post(
        "/process",
        json={
            "text": "Mam pytanie o urlop.",
            "source_channel": "API",
        },
    )

    response = client.get("/dashboard/tickets-by-day")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["count"] == 3