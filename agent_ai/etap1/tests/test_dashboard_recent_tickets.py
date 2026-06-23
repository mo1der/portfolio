from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_dashboard_recent_tickets_empty_database():
    response = client.get("/dashboard/recent-tickets")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert data["items"] == []


def test_dashboard_recent_tickets_after_process():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "API",
        },
    )

    assert process_response.status_code == 200

    response = client.get("/dashboard/recent-tickets")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert len(data["items"]) == 1

    ticket = data["items"][0]

    assert ticket["input_text"] == "Mam problem z fakturą."
    assert ticket["category"] == "FINANCE"
    assert ticket["priority"] == "HIGH"
    assert ticket["ticket_status"] == "NEW"
    assert ticket["source"] == "RULE_BASED"
    assert ticket["assigned_to"] == "finance_priority_team"
    assert "id" in ticket
    assert "created_at" in ticket


def test_dashboard_recent_tickets_limit():
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

    response = client.get("/dashboard/recent-tickets?limit=2")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2


def test_dashboard_recent_tickets_returns_newest_first():
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

    response = client.get("/dashboard/recent-tickets?limit=2")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2
    assert data["items"][0]["id"] > data["items"][1]["id"]