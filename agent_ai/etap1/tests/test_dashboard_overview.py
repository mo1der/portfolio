from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_dashboard_overview_empty_database():
    response = client.get("/dashboard/overview")

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert "status_counts" in data
    assert "category_counts" in data
    assert "priority_counts" in data
    assert "source_counts" in data
    assert "assigned_counts" in data
    assert "recent_tickets" in data
    assert "urgent_tickets" in data
    assert "unassigned_tickets" in data

    assert data["summary"]["total_tickets"] == 0
    assert data["status_counts"]["items"] == []
    assert data["category_counts"]["items"] == []
    assert data["priority_counts"]["items"] == []
    assert data["source_counts"]["items"] == []
    assert data["assigned_counts"]["items"] == []
    assert data["recent_tickets"]["items"] == []
    assert data["urgent_tickets"]["items"] == []
    assert data["unassigned_tickets"]["items"] == []


def test_dashboard_overview_after_process():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam pilny problem z fakturą.",
            "source_channel": "API",
        },
    )

    assert process_response.status_code == 200

    response = client.get("/dashboard/overview")

    assert response.status_code == 200

    data = response.json()

    assert data["summary"]["total_tickets"] == 1
    assert data["summary"]["new_tickets"] == 1
    assert data["summary"]["high_priority_tickets"] == 1
    assert data["summary"]["unassigned_tickets"] == 1
    assert data["summary"]["rule_based_tickets"] == 1

    assert {
        "name": "NEW",
        "count": 1,
    } in data["status_counts"]["items"]

    assert {
        "name": "FINANCE",
        "count": 1,
    } in data["category_counts"]["items"]

    assert {
        "name": "HIGH",
        "count": 1,
    } in data["priority_counts"]["items"]

    assert {
        "name": "RULE_BASED",
        "count": 1,
    } in data["source_counts"]["items"]

    assert {
        "name": "UNASSIGNED",
        "count": 1,
    } in data["assigned_counts"]["items"]

    assert len(data["recent_tickets"]["items"]) == 1
    assert len(data["urgent_tickets"]["items"]) == 1
    assert len(data["unassigned_tickets"]["items"]) == 1


def test_dashboard_overview_limit():
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

    response = client.get("/dashboard/overview?limit=2")

    assert response.status_code == 200

    data = response.json()

    assert data["summary"]["total_tickets"] == 3
    assert len(data["recent_tickets"]["items"]) == 2
    assert len(data["urgent_tickets"]["items"]) == 2
    assert len(data["unassigned_tickets"]["items"]) == 2