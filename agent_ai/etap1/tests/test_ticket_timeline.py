from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_ticket_timeline_empty_for_missing_ticket():
    response = client.get("/tickets/999999/timeline")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_ticket_timeline_contains_created_event():
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

    ticket_id = tickets_response.json()["items"][0]["id"]

    timeline_response = client.get(f"/tickets/{ticket_id}/timeline")

    assert timeline_response.status_code == 200

    data = timeline_response.json()

    assert "items" in data
    assert len(data["items"]) == 1

    item = data["items"][0]

    assert item["event_type"] == "CREATED"
    assert item["title"] == "Ticket created"
    assert item["description"] == "Mam problem z fakturą."
    assert item["author"] == "API"
    assert "created_at" in item


def test_ticket_timeline_contains_assignment_event():
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

    ticket_id = tickets_response.json()["items"][0]["id"]

    assign_response = client.patch(
        f"/tickets/{ticket_id}/assign",
        json={
            "assigned_to": "finance_team",
            "changed_by": "test_user",
            "note": "Przypisanie do finansów.",
        },
    )

    assert assign_response.status_code == 200

    timeline_response = client.get(f"/tickets/{ticket_id}/timeline")

    assert timeline_response.status_code == 200

    items = timeline_response.json()["items"]

    event_types = [item["event_type"] for item in items]

    assert "CREATED" in event_types
    assert "ASSIGNED" in event_types

    assignment_event = [
        item for item in items if item["event_type"] == "ASSIGNED"
    ][0]

    assert assignment_event["title"] == "Assigned: None -> finance_team"
    assert assignment_event["description"] == "Przypisanie do finansów."
    assert assignment_event["author"] == "test_user"


def test_ticket_timeline_contains_comment_event():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem.",
            "source_channel": "API",
        },
    )

    assert process_response.status_code == 200

    tickets_response = client.get(
        "/tickets?search=logowaniem&sort_by=id&sort_order=desc&limit=1"
    )

    assert tickets_response.status_code == 200

    ticket_id = tickets_response.json()["items"][0]["id"]

    comment_response = client.post(
        f"/tickets/{ticket_id}/comments",
        json={
            "comment_text": "Komentarz testowy timeline.",
            "author": "test_user",
        },
    )

    assert comment_response.status_code == 200

    timeline_response = client.get(f"/tickets/{ticket_id}/timeline")

    assert timeline_response.status_code == 200

    items = timeline_response.json()["items"]

    event_types = [item["event_type"] for item in items]

    assert "CREATED" in event_types
    assert "COMMENT_ADDED" in event_types

    comment_event = [
        item for item in items if item["event_type"] == "COMMENT_ADDED"
    ][0]

    assert comment_event["title"] == "Comment added"
    assert comment_event["description"] == "Komentarz testowy timeline."
    assert comment_event["author"] == "test_user"


def test_ticket_timeline_contains_status_event():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem.",
            "source_channel": "API",
        },
    )

    assert process_response.status_code == 200

    tickets_response = client.get(
        "/tickets?search=logowaniem&sort_by=id&sort_order=desc&limit=1"
    )

    assert tickets_response.status_code == 200

    ticket_id = tickets_response.json()["items"][0]["id"]

    status_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "IN_PROGRESS",
            "changed_by": "test_user",
            "note": "Rozpoczęcie pracy.",
        },
    )

    assert status_response.status_code == 200

    timeline_response = client.get(f"/tickets/{ticket_id}/timeline")

    assert timeline_response.status_code == 200

    items = timeline_response.json()["items"]

    event_types = [item["event_type"] for item in items]

    assert "CREATED" in event_types
    assert "STATUS_CHANGED" in event_types

    status_event = [
        item for item in items if item["event_type"] == "STATUS_CHANGED"
    ][0]

    assert status_event["title"] == "Status changed: NEW -> IN_PROGRESS"
    assert status_event["author"] == "test_user"
    assert status_event["description"] == "Rozpoczęcie pracy."


def test_ticket_timeline_is_sorted_by_created_at():
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

    ticket_id = tickets_response.json()["items"][0]["id"]

    client.patch(
        f"/tickets/{ticket_id}/assign",
        json={
            "assigned_to": "finance_team",
            "changed_by": "test_user",
            "note": "Przypisanie.",
        },
    )

    client.post(
        f"/tickets/{ticket_id}/comments",
        json={
            "comment_text": "Komentarz.",
            "author": "test_user",
        },
    )

    timeline_response = client.get(f"/tickets/{ticket_id}/timeline")

    assert timeline_response.status_code == 200

    items = timeline_response.json()["items"]

    dates = [item["created_at"] for item in items]

    assert dates == sorted(dates)