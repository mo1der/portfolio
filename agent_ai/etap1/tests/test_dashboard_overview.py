from datetime import datetime

from fastapi.testclient import TestClient

from app.database import Base, engine, SessionLocal
from app.main import app
from app.models import TicketHistory

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

def create_test_ticket(
    input_text: str,
    priority: str,
    ticket_status: str,
    sla_status: str | None = None,
):
    db = SessionLocal()

    ticket = TicketHistory(
        input_text=input_text,
        source_channel="API",
        category="FINANCE",
        priority=priority,
        intent="CREATE_TICKET",
        ticket_status=ticket_status,
        assigned_to=None,
        summary=input_text,
        suggested_action="Test action",
        source="RULE_BASED",
        sla_due_at=datetime.utcnow(),
        sla_status=sla_status,
        executed_action_type="CREATE_FINANCE_TICKET",
        executed_action_status="SIMULATED",
        executed_action_message="Test message",
        route_agent_name="finance_invoice_agent",
        route_department="FINANCE",
        route_reason="Test reason",
        route_action_type="CREATE_FINANCE_TICKET",
        created_at=datetime.utcnow(),
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    db.close()

    return ticket

def test_dashboard_summary_contains_sla_counts():
    create_test_ticket(
        input_text="Breached SLA ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="BREACHED",
    )

    create_test_ticket(
        input_text="Completed SLA ticket",
        priority="HIGH",
        ticket_status="CLOSED",
        sla_status="COMPLETED",
    )

    create_test_ticket(
        input_text="Active SLA ticket",
        priority="LOW",
        ticket_status="NEW",
        sla_status="ACTIVE",
    )

    response = client.get("/dashboard/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["breached_sla_tickets"] == 1
    assert data["completed_sla_tickets"] == 1
    assert data["active_sla_tickets"] == 1
    assert data["unknown_sla_tickets"] == 0