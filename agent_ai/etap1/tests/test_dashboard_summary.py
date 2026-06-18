from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_dashboard_summary_endpoint_returns_expected_structure():
    response = client.get("/dashboard/summary")

    assert response.status_code == 200

    data = response.json()

    assert "total_tickets" in data
    assert "new_tickets" in data
    assert "in_progress_tickets" in data
    assert "waiting_for_user_tickets" in data
    assert "resolved_tickets" in data
    assert "closed_tickets" in data
    assert "high_priority_tickets" in data
    assert "unassigned_tickets" in data
    assert "ai_classified_tickets" in data
    assert "rule_based_tickets" in data

    assert isinstance(data["total_tickets"], int)
    assert isinstance(data["new_tickets"], int)
    assert isinstance(data["in_progress_tickets"], int)
    assert isinstance(data["waiting_for_user_tickets"], int)
    assert isinstance(data["resolved_tickets"], int)
    assert isinstance(data["closed_tickets"], int)
    assert isinstance(data["high_priority_tickets"], int)
    assert isinstance(data["unassigned_tickets"], int)
    assert isinstance(data["ai_classified_tickets"], int)
    assert isinstance(data["rule_based_tickets"], int)


def test_dashboard_summary_total_increases_after_process():
    before_response = client.get("/dashboard/summary")
    assert before_response.status_code == 200

    before = before_response.json()

    process_response = client.post(
        "/process",
        json={
            "text": "Mam pilny problem z fakturą.",
            "source_channel": "API",
        },
    )

    assert process_response.status_code == 200

    after_response = client.get("/dashboard/summary")
    assert after_response.status_code == 200

    after = after_response.json()

    assert after["total_tickets"] == before["total_tickets"] + 1
    assert after["new_tickets"] == before["new_tickets"] + 1
    assert after["high_priority_tickets"] >= before["high_priority_tickets"]
    assert after["rule_based_tickets"] >= before["rule_based_tickets"]


def test_dashboard_summary_counts_status_change():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem.",
            "source_channel": "API",
        },
    )

    assert process_response.status_code == 200

    tickets_response = client.get(
        "/tickets?search=logowanie&sort_by=id&sort_order=desc&limit=1"
    )
    assert tickets_response.status_code == 200

    tickets = tickets_response.json()["items"]
    assert len(tickets) == 1

    ticket_id = tickets[0]["id"]

    before_response = client.get("/dashboard/summary")
    assert before_response.status_code == 200

    before = before_response.json()

    status_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "IN_PROGRESS",
            "changed_by": "test_user",
            "note": "Test zmiany statusu dla dashboard summary.",
        },
    )

    assert status_response.status_code == 200

    after_response = client.get("/dashboard/summary")
    assert after_response.status_code == 200

    after = after_response.json()

    assert after["new_tickets"] == before["new_tickets"] - 1
    assert after["in_progress_tickets"] == before["in_progress_tickets"] + 1