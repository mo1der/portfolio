from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_dashboard_urgent_tickets_empty_database():
    response = client.get("/dashboard/urgent-tickets")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert data["items"] == []


def test_dashboard_urgent_tickets_after_high_priority_ticket():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam pilny problem z fakturą.",
            "source_channel": "API",
        },
    )

    assert process_response.status_code == 200

    response = client.get("/dashboard/urgent-tickets")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1

    ticket = data["items"][0]

    assert ticket["priority"] == "HIGH"
    assert ticket["ticket_status"] != "CLOSED"


def test_dashboard_urgent_tickets_does_not_return_closed_ticket():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam pilny problem z fakturą.",
            "source_channel": "API",
        },
    )

    assert process_response.status_code == 200

    tickets_response = client.get(
        "/tickets?search=fakturą&sort_by=id&sort_order=desc&limit=1"
    )

    assert tickets_response.status_code == 200

    tickets = tickets_response.json()["items"]
    assert len(tickets) == 1

    ticket_id = tickets[0]["id"]

    in_progress_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "IN_PROGRESS",
            "changed_by": "test_user",
            "note": "Przejście do IN_PROGRESS w teście urgent tickets.",
        },
    )

    assert in_progress_response.status_code == 200

    resolved_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "RESOLVED",
            "changed_by": "test_user",
            "note": "Przejście do RESOLVED w teście urgent tickets.",
        },
    )

    assert resolved_response.status_code == 200

    closed_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "CLOSED",
            "changed_by": "test_user",
            "note": "Zamknięcie ticketa w teście urgent tickets.",
        },
    )

    assert closed_response.status_code == 200

    response = client.get("/dashboard/urgent-tickets")

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []


def test_dashboard_urgent_tickets_limit():
    client.post(
        "/process",
        json={
            "text": "Mam pilny problem z fakturą.",
            "source_channel": "API",
        },
    )

    client.post(
        "/process",
        json={
            "text": "Mam pilny problem z logowaniem.",
            "source_channel": "API",
        },
    )

    client.post(
        "/process",
        json={
            "text": "Mam pilny problem z urlopem.",
            "source_channel": "API",
        },
    )

    response = client.get("/dashboard/urgent-tickets?limit=2")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2


def test_dashboard_urgent_tickets_returns_newest_first():
    client.post(
        "/process",
        json={
            "text": "Mam pilny problem z fakturą.",
            "source_channel": "API",
        },
    )

    client.post(
        "/process",
        json={
            "text": "Mam pilny problem z logowaniem.",
            "source_channel": "API",
        },
    )

    response = client.get("/dashboard/urgent-tickets?limit=2")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2
    assert data["items"][0]["id"] > data["items"][1]["id"]