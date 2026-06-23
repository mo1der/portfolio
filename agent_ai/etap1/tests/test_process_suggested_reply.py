from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_process_creates_ticket_with_suggested_reply():
    response = client.post(
        "/process",
        json={
            "text": "Mam pilny problem z fakturą.",
            "source_channel": "API",
        },
    )

    assert response.status_code == 200

    tickets_response = client.get("/tickets?category=FINANCE&priority=HIGH")

    assert tickets_response.status_code == 200

    data = tickets_response.json()
    items = data["items"]

    assert len(items) == 1

    ticket = items[0]

    assert ticket["category"] == "FINANCE"
    assert ticket["priority"] == "HIGH"
    assert ticket["assigned_to"] == "finance_priority_team"
    assert ticket["suggested_reply"] is not None
    assert "finansów" in ticket["suggested_reply"]
    assert "finance_priority_team" in ticket["suggested_reply"]


def test_get_ticket_by_id_returns_suggested_reply():
    response = client.post(
        "/process",
        json={
            "text": "Nie mogę zalogować się do systemu.",
            "source_channel": "API",
        },
    )

    assert response.status_code == 200

    tickets_response = client.get("/tickets?category=IT_SUPPORT&priority=HIGH")

    assert tickets_response.status_code == 200

    ticket = tickets_response.json()["items"][0]
    ticket_id = ticket["id"]

    detail_response = client.get(f"/tickets/{ticket_id}")

    assert detail_response.status_code == 200

    detail = detail_response.json()

    assert detail["suggested_reply"] is not None
    assert "it_priority_team" in detail["suggested_reply"]