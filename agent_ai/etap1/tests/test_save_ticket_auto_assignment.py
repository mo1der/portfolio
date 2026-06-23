from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_process_endpoint_auto_assigns_finance_high_ticket():
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
    assert items[0]["category"] == "FINANCE"
    assert items[0]["priority"] == "HIGH"
    assert items[0]["assigned_to"] == "finance_priority_team"


def test_process_endpoint_auto_assigns_it_high_ticket():
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

    data = tickets_response.json()
    items = data["items"]

    assert len(items) == 1
    assert items[0]["category"] == "IT_SUPPORT"
    assert items[0]["priority"] == "HIGH"
    assert items[0]["assigned_to"] == "it_priority_team"


def test_process_endpoint_auto_assigns_hr_ticket():
    response = client.post(
        "/process",
        json={
            "text": "Chciałbym zapytać o urlop.",
            "source_channel": "API",
        },
    )

    assert response.status_code == 200

    tickets_response = client.get("/tickets?category=HR")

    assert tickets_response.status_code == 200

    data = tickets_response.json()
    items = data["items"]

    assert len(items) == 1
    assert items[0]["category"] == "HR"
    assert items[0]["assigned_to"] in [
        "hr_team",
        "hr_priority_team",
    ]