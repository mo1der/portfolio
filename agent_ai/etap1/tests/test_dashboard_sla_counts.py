from datetime import datetime

from fastapi.testclient import TestClient

from app.database import Base, engine, SessionLocal
from app.main import app
from app.models import TicketHistory

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def create_test_ticket(
    input_text: str,
    sla_status: str | None,
):
    db = SessionLocal()

    ticket = TicketHistory(
        input_text=input_text,
        source_channel="API",
        category="FINANCE",
        priority="HIGH",
        intent="CREATE_TICKET",
        ticket_status="NEW",
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


def get_count_by_name(items, name: str):
    for item in items:
        if item["name"] == name:
            return item["count"]

    return None


def test_dashboard_sla_counts_empty_database():
    response = client.get("/dashboard/sla-counts")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert get_count_by_name(data["items"], "BREACHED") == 0
    assert get_count_by_name(data["items"], "ACTIVE") == 0
    assert get_count_by_name(data["items"], "COMPLETED") == 0
    assert get_count_by_name(data["items"], "UNKNOWN") == 0


def test_dashboard_sla_counts_returns_counts_by_sla_status():
    create_test_ticket(
        input_text="Breached SLA ticket",
        sla_status="BREACHED",
    )

    create_test_ticket(
        input_text="Active SLA ticket",
        sla_status="ACTIVE",
    )

    create_test_ticket(
        input_text="Completed SLA ticket",
        sla_status="COMPLETED",
    )

    create_test_ticket(
        input_text="Unknown SLA ticket",
        sla_status="UNKNOWN",
    )

    response = client.get("/dashboard/sla-counts")

    assert response.status_code == 200

    data = response.json()

    assert get_count_by_name(data["items"], "BREACHED") == 1
    assert get_count_by_name(data["items"], "ACTIVE") == 1
    assert get_count_by_name(data["items"], "COMPLETED") == 1
    assert get_count_by_name(data["items"], "UNKNOWN") == 1


def test_dashboard_sla_counts_treats_null_and_empty_as_unknown():
    create_test_ticket(
        input_text="Null SLA ticket",
        sla_status=None,
    )

    create_test_ticket(
        input_text="Empty SLA ticket",
        sla_status="",
    )

    create_test_ticket(
        input_text="Active SLA ticket",
        sla_status="ACTIVE",
    )

    response = client.get("/dashboard/sla-counts")

    assert response.status_code == 200

    data = response.json()

    assert get_count_by_name(data["items"], "UNKNOWN") == 2
    assert get_count_by_name(data["items"], "ACTIVE") == 1