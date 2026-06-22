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
    sla_due_at: datetime | None,
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

    ticket_id = ticket.id

    db.close()

    return ticket_id


def get_ticket(ticket_id: int):
    db = SessionLocal()
    ticket = db.query(TicketHistory).filter(TicketHistory.id == ticket_id).first()
    db.close()

    return ticket


def test_recalculate_sla_changes_active_to_breached_when_due_date_passed():
    ticket_id = create_test_ticket(
        input_text="Expired active SLA ticket",
        priority="HIGH",
        ticket_status="NEW",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() - timedelta(hours=1),
    )

    response = client.post("/tickets/sla/recalculate")

    assert response.status_code == 200

    data = response.json()

    assert data["checked_tickets"] == 1
    assert data["updated_tickets"] == 1

    ticket = get_ticket(ticket_id)

    assert ticket.sla_status == "BREACHED"


def test_recalculate_sla_keeps_active_when_due_date_is_future():
    ticket_id = create_test_ticket(
        input_text="Future active SLA ticket",
        priority="LOW",
        ticket_status="NEW",
        sla_status="ACTIVE",
        sla_due_at=datetime.utcnow() + timedelta(hours=10),
    )

    response = client.post("/tickets/sla/recalculate")

    assert response.status_code == 200

    data = response.json()

    assert data["checked_tickets"] == 1
    assert data["updated_tickets"] == 0

    ticket = get_ticket(ticket_id)

    assert ticket.sla_status == "ACTIVE"


def test_recalculate_sla_sets_completed_for_closed_ticket():
    ticket_id = create_test_ticket(
        input_text="Closed SLA ticket",
        priority="HIGH",
        ticket_status="CLOSED",
        sla_status="BREACHED",
        sla_due_at=datetime.utcnow() - timedelta(hours=10),
    )

    response = client.post("/tickets/sla/recalculate")

    assert response.status_code == 200

    data = response.json()

    assert data["checked_tickets"] == 1
    assert data["updated_tickets"] == 1

    ticket = get_ticket(ticket_id)

    assert ticket.sla_status == "COMPLETED"


def test_recalculate_sla_sets_unknown_when_due_date_is_missing():
    ticket_id = create_test_ticket(
        input_text="Missing SLA due date ticket",
        priority="MEDIUM",
        ticket_status="NEW",
        sla_status="ACTIVE",
        sla_due_at=None,
    )

    response = client.post("/tickets/sla/recalculate")

    assert response.status_code == 200

    data = response.json()

    assert data["checked_tickets"] == 1
    assert data["updated_tickets"] == 1

    ticket = get_ticket(ticket_id)

    assert ticket.sla_status == "UNKNOWN"


def test_recalculate_sla_handles_empty_database():
    response = client.post("/tickets/sla/recalculate")

    assert response.status_code == 200

    data = response.json()

    assert data["checked_tickets"] == 0
    assert data["updated_tickets"] == 0