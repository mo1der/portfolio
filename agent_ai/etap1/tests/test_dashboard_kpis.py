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
    source: str,
    sla_status: str | None,
    assigned_to: str | None,
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
        source=source,
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


def test_dashboard_kpis_empty_database():
    response = client.get("/dashboard/kpis")

    assert response.status_code == 200

    data = response.json()

    assert data["total_tickets"] == 0
    assert data["open_tickets"] == 0
    assert data["closed_or_resolved_tickets"] == 0
    assert data["high_priority_tickets"] == 0
    assert data["breached_sla_tickets"] == 0
    assert data["active_sla_tickets"] == 0
    assert data["unassigned_tickets"] == 0
    assert data["assigned_tickets"] == 0
    assert data["ai_classification_rate"] == 0.0
    assert data["rule_based_classification_rate"] == 0.0
    assert data["auto_assignment_rate"] == 0.0


def test_dashboard_kpis_returns_manager_metrics():
    create_test_ticket(
        input_text="AI breached high ticket",
        priority="HIGH",
        ticket_status="NEW",
        source="AI",
        sla_status="BREACHED",
        assigned_to="finance_priority_team",
    )

    create_test_ticket(
        input_text="Rule active medium ticket",
        priority="MEDIUM",
        ticket_status="IN_PROGRESS",
        source="RULE_BASED",
        sla_status="ACTIVE",
        assigned_to="finance_team",
    )

    create_test_ticket(
        input_text="Rule completed ticket",
        priority="LOW",
        ticket_status="CLOSED",
        source="RULE_BASED",
        sla_status="COMPLETED",
        assigned_to=None,
    )

    response = client.get("/dashboard/kpis")

    assert response.status_code == 200

    data = response.json()

    assert data["total_tickets"] == 3
    assert data["open_tickets"] == 2
    assert data["closed_or_resolved_tickets"] == 1
    assert data["high_priority_tickets"] == 1
    assert data["breached_sla_tickets"] == 1
    assert data["active_sla_tickets"] == 1
    assert data["unassigned_tickets"] == 1
    assert data["assigned_tickets"] == 2

    assert data["ai_classification_rate"] == 33.33
    assert data["rule_based_classification_rate"] == 66.67
    assert data["auto_assignment_rate"] == 66.67


def test_dashboard_kpis_counts_resolved_as_closed_or_resolved():
    create_test_ticket(
        input_text="Resolved ticket",
        priority="HIGH",
        ticket_status="RESOLVED",
        source="RULE_BASED",
        sla_status="COMPLETED",
        assigned_to="finance_team",
    )

    create_test_ticket(
        input_text="Closed ticket",
        priority="HIGH",
        ticket_status="CLOSED",
        source="RULE_BASED",
        sla_status="COMPLETED",
        assigned_to="finance_team",
    )

    create_test_ticket(
        input_text="Open ticket",
        priority="HIGH",
        ticket_status="NEW",
        source="AI",
        sla_status="ACTIVE",
        assigned_to="finance_priority_team",
    )

    response = client.get("/dashboard/kpis")

    assert response.status_code == 200

    data = response.json()

    assert data["total_tickets"] == 3
    assert data["open_tickets"] == 1
    assert data["closed_or_resolved_tickets"] == 2