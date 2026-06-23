from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_process_complex_creates_multiple_tickets():
    response = client.post(
        "/process/complex",
        json={
            "text": (
                "Mam problem z fakturą, "
                "nie mogę się zalogować i "
                "chcę zgłosić urlop"
            ),
            "source_channel": "API",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_complex"] is True
    assert len(data["created_tickets"]) == 3

    categories = [
        ticket["category"]
        for ticket in data["created_tickets"]
    ]

    assert "FINANCE" in categories
    assert "IT_SUPPORT" in categories
    assert "HR" in categories


def test_process_complex_single_message_creates_one_ticket():
    response = client.post(
        "/process/complex",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "API",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_complex"] is False
    assert len(data["created_tickets"]) == 1
    assert data["created_tickets"][0]["category"] == "FINANCE"


def test_process_complex_ticket_contains_assignment_and_sla_data():
    response = client.post(
        "/process/complex",
        json={
            "text": "Mam pilny problem z fakturą i nie mogę się zalogować",
            "source_channel": "API",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_complex"] is True
    assert len(data["created_tickets"]) == 2

    for ticket in data["created_tickets"]:
        assert ticket["assigned_to"] is not None
        assert ticket["ticket_status"] == "NEW"
        assert ticket["suggested_action"] is not None


def test_process_complex_creates_tickets_visible_in_ticket_list():
    response = client.post(
        "/process/complex",
        json={
            "text": "Mam problem z fakturą i nie mogę się zalogować",
            "source_channel": "API",
        },
    )

    assert response.status_code == 200

    tickets_response = client.get("/tickets?limit=10")

    assert tickets_response.status_code == 200

    data = tickets_response.json()

    assert data["total"] == 2

    categories = [
        item["category"]
        for item in data["items"]
    ]

    assert "FINANCE" in categories
    assert "IT_SUPPORT" in categories