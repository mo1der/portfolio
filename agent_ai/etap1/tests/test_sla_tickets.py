from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.database import Base, engine, SessionLocal
from app.main import app
from app.models import TicketHistory

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_ticket(
    *,
    input_text: str,
    priority: str,
    ticket_status: str,
    sla_due_at,
    sla_status: str,
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


def test_get_breached_sla_tickets_returns_only_breached():
    now = datetime.utcnow()

    breached_ticket = create_ticket(
        input_text="Breached SLA ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_due_at=now - timedelta(hours=1),
        sla_status="BREACHED",
    )

    create_ticket(
        input_text="Active SLA ticket",
        priority="LOW",
        ticket_status="NEW",
        sla_due_at=now + timedelta(hours=24),
        sla_status="ACTIVE",
    )

    response = client.get("/tickets/sla/breached")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == breached_ticket.id
    assert data[0]["sla_status"] == "BREACHED"


def test_get_breached_sla_tickets_respects_limit():
    now = datetime.utcnow()

    create_ticket(
        input_text="Breached SLA ticket 1",
        priority="HIGH",
        ticket_status="NEW",
        sla_due_at=now - timedelta(hours=3),
        sla_status="BREACHED",
    )

    create_ticket(
        input_text="Breached SLA ticket 2",
        priority="HIGH",
        ticket_status="NEW",
        sla_due_at=now - timedelta(hours=2),
        sla_status="BREACHED",
    )

    response = client.get("/tickets/sla/breached?limit=1")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["sla_status"] == "BREACHED"


def test_get_breached_sla_tickets_orders_by_sla_due_at_asc():
    now = datetime.utcnow()

    later_ticket = create_ticket(
        input_text="Later breached ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_due_at=now - timedelta(hours=1),
        sla_status="BREACHED",
    )

    earlier_ticket = create_ticket(
        input_text="Earlier breached ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_due_at=now - timedelta(hours=5),
        sla_status="BREACHED",
    )

    response = client.get("/tickets/sla/breached")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["id"] == earlier_ticket.id
    assert data[1]["id"] == later_ticket.id