from datetime import datetime

from app.database import Base, engine, SessionLocal
from app.duplicate_detector import (
    calculate_similarity,
    find_possible_duplicate_ticket,
)
from app.models import TicketHistory


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def create_test_ticket(input_text: str, category: str = "FINANCE"):
    db = SessionLocal()

    ticket = TicketHistory(
        input_text=input_text,
        source_channel="API",
        category=category,
        priority="HIGH",
        intent="CREATE_TICKET",
        ticket_status="NEW",
        assigned_to="finance_priority_team",
        summary=input_text,
        suggested_action="Test action",
        suggested_reply="Test reply",
        suggested_reply_source="RULE_BASED",
        possible_duplicate=False,
        duplicate_ticket_id=None,
        duplicate_score=None,
        source="RULE_BASED",
        sla_due_at=datetime.utcnow(),
        sla_status="ACTIVE",
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


def test_calculate_similarity_for_identical_texts():
    score = calculate_similarity(
        "Mam problem z fakturą.",
        "Mam problem z fakturą.",
    )

    assert score == 1.0


def test_calculate_similarity_for_different_texts():
    score = calculate_similarity(
        "Mam problem z fakturą.",
        "Nie mogę zalogować się do systemu.",
    )

    assert score < 0.75


def test_find_possible_duplicate_ticket_returns_duplicate():
    existing_ticket = create_test_ticket(
        input_text="Mam problem z fakturą za ostatni miesiąc.",
        category="FINANCE",
    )

    db = SessionLocal()

    result = find_possible_duplicate_ticket(
        db=db,
        input_text="Mam problem z fakturą za ostatni miesiąc.",
        category="FINANCE",
    )

    db.close()

    assert result["possible_duplicate"] is True
    assert result["duplicate_ticket_id"] == existing_ticket.id
    assert result["duplicate_score"] == 1.0


def test_find_possible_duplicate_ticket_ignores_other_category():
    create_test_ticket(
        input_text="Mam problem z fakturą za ostatni miesiąc.",
        category="IT_SUPPORT",
    )

    db = SessionLocal()

    result = find_possible_duplicate_ticket(
        db=db,
        input_text="Mam problem z fakturą za ostatni miesiąc.",
        category="FINANCE",
    )

    db.close()

    assert result["possible_duplicate"] is False
    assert result["duplicate_ticket_id"] is None


def test_find_possible_duplicate_ticket_returns_best_match():
    worse_ticket = create_test_ticket(
        input_text="Mam pytanie o płatność.",
        category="FINANCE",
    )

    best_ticket = create_test_ticket(
        input_text="Mam problem z fakturą za maj.",
        category="FINANCE",
    )

    db = SessionLocal()

    result = find_possible_duplicate_ticket(
        db=db,
        input_text="Mam problem z fakturą za maj.",
        category="FINANCE",
    )

    db.close()

    assert result["possible_duplicate"] is True
    assert result["duplicate_ticket_id"] == best_ticket.id
    assert result["duplicate_ticket_id"] != worse_ticket.id