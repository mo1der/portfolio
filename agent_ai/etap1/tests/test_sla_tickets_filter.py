from datetime import datetime, timedelta

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
    sla_due_at: datetime,
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
        sla_due_at=sla_due_at,
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


def test_get_sla_tickets_filters_breached_status():
    create_test_ticket(
        input_text="Breached SLA ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="BREACHED",
        sla_due_at=datetime.utcnow() - timedelta(hours=1),
    )

    create_test_ticket(
        input_text="Active SLA ticket",
        priority="LOW",
        ticket_status="NEW",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() + timedelta(hours=10),
    )

    response = client.get("/tickets/sla?status=BREACHED")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["input_text"] == "Breached SLA ticket"
    assert data[0]["sla_status"] == "BREACHED"


def test_get_sla_tickets_filters_active_status():
    create_test_ticket(
        input_text="Breached SLA ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="BREACHED",
        sla_due_at=datetime.utcnow() - timedelta(hours=1),
    )

    create_test_ticket(
        input_text="Active SLA ticket",
        priority="LOW",
        ticket_status="NEW",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() + timedelta(hours=10),
    )

    response = client.get("/tickets/sla?status=ACTIVE")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["input_text"] == "Active SLA ticket"
    assert data[0]["sla_status"] == "ACTIVE"


def test_get_sla_tickets_respects_limit():
    create_test_ticket(
        input_text="First SLA ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="BREACHED",
        sla_due_at=datetime.utcnow() - timedelta(hours=2),
    )

    create_test_ticket(
        input_text="Second SLA ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="BREACHED",
        sla_due_at=datetime.utcnow() - timedelta(hours=1),
    )

    response = client.get("/tickets/sla?status=BREACHED&limit=1")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1


def test_get_sla_tickets_rejects_invalid_status():
    response = client.get("/tickets/sla?status=WRONG")

    assert response.status_code == 422


def test_get_sla_tickets_sorts_by_sla_due_at():
    create_test_ticket(
        input_text="Second due ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="BREACHED",
        sla_due_at=datetime.utcnow() + timedelta(hours=2),
    )

    create_test_ticket(
        input_text="First due ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="BREACHED",
        sla_due_at=datetime.utcnow() + timedelta(hours=1),
    )

    response = client.get("/tickets/sla?status=BREACHED")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["input_text"] == "First due ticket"
    assert data[1]["input_text"] == "Second due ticket"


def test_get_sla_tickets_filters_unknown_status():
    create_test_ticket(
        input_text="Unknown SLA ticket",
        priority="MEDIUM",
        ticket_status="NEW",
        sla_status="UNKNOWN",
        sla_due_at=datetime.utcnow(),
    )

    create_test_ticket(
        input_text="Active SLA ticket",
        priority="LOW",
        ticket_status="NEW",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() + timedelta(hours=10),
    )

    response = client.get("/tickets/sla?status=UNKNOWN")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["input_text"] == "Unknown SLA ticket"
    assert data[0]["sla_status"] == "UNKNOWN"