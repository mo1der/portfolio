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
    sla_status: str | None,
    sla_due_at: datetime | None,
    ticket_status: str = "NEW",
):
    db = SessionLocal()

    ticket = TicketHistory(
        input_text=input_text,
        source_channel="API",
        category="FINANCE",
        priority="HIGH",
        intent="CREATE_TICKET",
        ticket_status=ticket_status,
        assigned_to="finance_priority_team",
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


def test_due_soon_sla_tickets_returns_active_ticket_due_within_hours():
    create_test_ticket(
        input_text="Due soon active ticket",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() + timedelta(hours=2),
    )

    create_test_ticket(
        input_text="Future active ticket",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() + timedelta(hours=10),
    )

    response = client.get("/tickets/sla/due-soon?hours=4")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["input_text"] == "Due soon active ticket"
    assert data[0]["sla_status"] == "ACTIVE"


def test_due_soon_sla_tickets_excludes_breached_ticket():
    create_test_ticket(
        input_text="Breached ticket",
        sla_status="BREACHED",
        sla_due_at=datetime.utcnow() - timedelta(hours=1),
    )

    create_test_ticket(
        input_text="Due soon active ticket",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() + timedelta(hours=2),
    )

    response = client.get("/tickets/sla/due-soon?hours=4")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["input_text"] == "Due soon active ticket"


def test_due_soon_sla_tickets_excludes_completed_ticket():
    create_test_ticket(
        input_text="Completed ticket",
        sla_status="COMPLETED",
        sla_due_at=datetime.utcnow() + timedelta(hours=2),
        ticket_status="CLOSED",
    )

    create_test_ticket(
        input_text="Due soon active ticket",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() + timedelta(hours=2),
    )

    response = client.get("/tickets/sla/due-soon?hours=4")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["input_text"] == "Due soon active ticket"


def test_due_soon_sla_tickets_respects_limit():
    create_test_ticket(
        input_text="First due soon ticket",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() + timedelta(hours=1),
    )

    create_test_ticket(
        input_text="Second due soon ticket",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() + timedelta(hours=2),
    )

    response = client.get("/tickets/sla/due-soon?hours=4&limit=1")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["input_text"] == "First due soon ticket"


def test_due_soon_sla_tickets_sorts_by_sla_due_at():
    create_test_ticket(
        input_text="Second due ticket",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() + timedelta(hours=3),
    )

    create_test_ticket(
        input_text="First due ticket",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() + timedelta(hours=1),
    )

    response = client.get("/tickets/sla/due-soon?hours=4")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["input_text"] == "First due ticket"
    assert data[1]["input_text"] == "Second due ticket"


def test_due_soon_sla_tickets_rejects_invalid_hours():
    response = client.get("/tickets/sla/due-soon?hours=0")

    assert response.status_code == 422


def test_due_soon_sla_tickets_rejects_invalid_limit():
    response = client.get("/tickets/sla/due-soon?limit=0")

    assert response.status_code == 422