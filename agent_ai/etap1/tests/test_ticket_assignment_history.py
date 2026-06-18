from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_assignment_history_empty_for_new_ticket():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
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

    history_response = client.get(f"/tickets/{ticket_id}/assignment-history")

    assert history_response.status_code == 200
    assert history_response.json() == []


def test_assignment_history_created_after_assign():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
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

    assign_response = client.patch(
        f"/tickets/{ticket_id}/assign",
        json={
            "assigned_to": "finance_team",
            "changed_by": "test_user",
            "note": "Przypisanie testowe do działu finansów.",
        },
    )

    assert assign_response.status_code == 200

    history_response = client.get(f"/tickets/{ticket_id}/assignment-history")

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1

    item = history[0]

    assert item["ticket_id"] == ticket_id
    assert item["old_assigned_to"] is None
    assert item["new_assigned_to"] == "finance_team"
    assert item["changed_by"] == "test_user"
    assert item["note"] == "Przypisanie testowe do działu finansów."
    assert "created_at" in item


def test_assignment_history_tracks_reassignment():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
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

    first_assign_response = client.patch(
        f"/tickets/{ticket_id}/assign",
        json={
            "assigned_to": "finance_team",
            "changed_by": "test_user",
            "note": "Pierwsze przypisanie.",
        },
    )

    assert first_assign_response.status_code == 200

    second_assign_response = client.patch(
        f"/tickets/{ticket_id}/assign",
        json={
            "assigned_to": "senior_finance_team",
            "changed_by": "manager",
            "note": "Przekazanie do senior finance.",
        },
    )

    assert second_assign_response.status_code == 200

    history_response = client.get(f"/tickets/{ticket_id}/assignment-history")

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 2

    assert history[0]["old_assigned_to"] is None
    assert history[0]["new_assigned_to"] == "finance_team"

    assert history[1]["old_assigned_to"] == "finance_team"
    assert history[1]["new_assigned_to"] == "senior_finance_team"
    assert history[1]["changed_by"] == "manager"
    assert history[1]["note"] == "Przekazanie do senior finance."


def test_assignment_history_returns_404_for_missing_ticket():
    response = client.get("/tickets/999999/assignment-history")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"