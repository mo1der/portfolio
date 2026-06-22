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
    priority: str,
    ticket_status: str,
    sla_status: str | None,
    assigned_to: str | None = None,
):
    db = SessionLocal()

    ticket = TicketHistory(
        input_text=input_text,
        source_channel="API",
        category="FINANCE",
        priority=priority,
        intent="CREATE_TICKET",
        ticket_status=ticket_status,
        assigned_to=assigned_to,
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


def test_get_tickets_filters_by_breached_sla_status():
    create_test_ticket(
        input_text="Breached SLA ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="BREACHED",
    )

    create_test_ticket(
        input_text="Active SLA ticket",
        priority="LOW",
        ticket_status="NEW",
        sla_status="ACTIVE",
    )

    response = client.get("/tickets?sla_status=BREACHED")

    assert response.status_code == 200

    data = response.json()
    items = data["items"]

    assert len(items) == 1
    assert items[0]["input_text"] == "Breached SLA ticket"
    assert items[0]["sla_status"] == "BREACHED"


def test_get_tickets_filters_by_active_sla_status():
    create_test_ticket(
        input_text="Breached SLA ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="BREACHED",
    )

    create_test_ticket(
        input_text="Active SLA ticket",
        priority="LOW",
        ticket_status="NEW",
        sla_status="ACTIVE",
    )

    response = client.get("/tickets?sla_status=ACTIVE")

    assert response.status_code == 200

    data = response.json()
    items = data["items"]

    assert len(items) == 1
    assert items[0]["input_text"] == "Active SLA ticket"
    assert items[0]["sla_status"] == "ACTIVE"


def test_get_tickets_filters_by_unknown_sla_status():
    create_test_ticket(
        input_text="Unknown SLA ticket",
        priority="MEDIUM",
        ticket_status="NEW",
        sla_status="UNKNOWN",
    )

    create_test_ticket(
        input_text="Active SLA ticket",
        priority="LOW",
        ticket_status="NEW",
        sla_status="ACTIVE",
    )

    response = client.get("/tickets?sla_status=UNKNOWN")

    assert response.status_code == 200

    data = response.json()
    items = data["items"]

    assert len(items) == 1
    assert items[0]["input_text"] == "Unknown SLA ticket"
    assert items[0]["sla_status"] == "UNKNOWN"


def test_get_tickets_filters_by_null_and_empty_sla_as_unknown():
    create_test_ticket(
        input_text="Null SLA ticket",
        priority="MEDIUM",
        ticket_status="NEW",
        sla_status=None,
    )

    create_test_ticket(
        input_text="Empty SLA ticket",
        priority="MEDIUM",
        ticket_status="NEW",
        sla_status="",
    )

    create_test_ticket(
        input_text="Active SLA ticket",
        priority="LOW",
        ticket_status="NEW",
        sla_status="ACTIVE",
    )

    response = client.get("/tickets?sla_status=UNKNOWN")

    assert response.status_code == 200

    data = response.json()
    items = data["items"]

    assert len(items) == 2

    input_texts = [item["input_text"] for item in items]

    assert "Null SLA ticket" in input_texts
    assert "Empty SLA ticket" in input_texts


def test_get_tickets_combines_priority_and_sla_status_filters():
    create_test_ticket(
        input_text="High breached ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="BREACHED",
    )

    create_test_ticket(
        input_text="Low breached ticket",
        priority="LOW",
        ticket_status="NEW",
        sla_status="BREACHED",
    )

    create_test_ticket(
        input_text="High active ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="ACTIVE",
    )

    response = client.get("/tickets?priority=HIGH&sla_status=BREACHED")

    assert response.status_code == 200

    data = response.json()
    items = data["items"]

    assert len(items) == 1
    assert items[0]["input_text"] == "High breached ticket"
    assert items[0]["priority"] == "HIGH"
    assert items[0]["sla_status"] == "BREACHED"


def test_get_tickets_combines_ticket_status_and_sla_status_filters():
    create_test_ticket(
        input_text="New breached ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="BREACHED",
    )

    create_test_ticket(
        input_text="In progress breached ticket",
        priority="HIGH",
        ticket_status="IN_PROGRESS",
        sla_status="BREACHED",
    )

    response = client.get("/tickets?status=NEW&sla_status=BREACHED")

    assert response.status_code == 200

    data = response.json()
    items = data["items"]

    assert len(items) == 1
    assert items[0]["input_text"] == "New breached ticket"
    assert items[0]["ticket_status"] == "NEW"
    assert items[0]["sla_status"] == "BREACHED"


def test_get_tickets_rejects_invalid_sla_status():
    response = client.get("/tickets?sla_status=WRONG")

    assert response.status_code == 422