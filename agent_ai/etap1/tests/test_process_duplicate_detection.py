from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_process_marks_second_similar_ticket_as_possible_duplicate():
    first_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą za ostatni miesiąc.",
            "source_channel": "API",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą za ostatni miesiąc.",
            "source_channel": "API",
        },
    )

    assert second_response.status_code == 200

    tickets_response = client.get(
        "/tickets?category=FINANCE&priority=HIGH&limit=2&sort_by=created_at&sort_order=desc"
    )

    assert tickets_response.status_code == 200

    data = tickets_response.json()
    items = data["items"]

    assert len(items) == 2

    newest_ticket = items[0]
    older_ticket = items[1]

    assert newest_ticket["possible_duplicate"] is True
    assert newest_ticket["duplicate_ticket_id"] == older_ticket["id"]
    assert newest_ticket["duplicate_score"] == 1.0


def test_process_does_not_mark_different_ticket_as_duplicate():
    first_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą za ostatni miesiąc.",
            "source_channel": "API",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/process",
        json={
            "text": "Nie mogę zalogować się do systemu.",
            "source_channel": "API",
        },
    )

    assert second_response.status_code == 200

    tickets_response = client.get(
        "/tickets?limit=2&sort_by=created_at&sort_order=desc"
    )

    assert tickets_response.status_code == 200

    data = tickets_response.json()
    newest_ticket = data["items"][0]

    assert newest_ticket["possible_duplicate"] is False
    assert newest_ticket["duplicate_ticket_id"] is None