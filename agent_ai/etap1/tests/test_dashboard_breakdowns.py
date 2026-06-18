from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_dashboard_status_counts_empty_database():
    response = client.get("/dashboard/status-counts")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert data["items"] == []


def test_dashboard_status_counts_after_process():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "API",
        },
    )

    assert process_response.status_code == 200

    response = client.get("/dashboard/status-counts")

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == [
        {
            "name": "NEW",
            "count": 1,
        }
    ]


def test_dashboard_category_counts_after_process():
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

    response = client.get("/dashboard/category-counts")

    assert response.status_code == 200

    data = response.json()

    items = data["items"]

    assert {
        "name": "FINANCE",
        "count": 1,
    } in items

    assert {
        "name": "IT_SUPPORT",
        "count": 1,
    } in items


def test_dashboard_priority_counts_after_process():
    client.post(
        "/process",
        json={
            "text": "Mam pilny problem z fakturą.",
            "source_channel": "API",
        },
    )

    response = client.get("/dashboard/priority-counts")

    assert response.status_code == 200

    data = response.json()

    assert {
        "name": "HIGH",
        "count": 1,
    } in data["items"]


def test_dashboard_source_counts_after_process():
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "API",
        },
    )

    response = client.get("/dashboard/source-counts")

    assert response.status_code == 200

    data = response.json()

    assert {
        "name": "RULE_BASED",
        "count": 1,
    } in data["items"]


def test_dashboard_assigned_counts_for_unassigned_ticket():
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "API",
        },
    )

    response = client.get("/dashboard/assigned-counts")

    assert response.status_code == 200

    data = response.json()

    assert {
        "name": "UNASSIGNED",
        "count": 1,
    } in data["items"]