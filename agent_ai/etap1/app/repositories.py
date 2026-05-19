from typing import Any

from sqlalchemy.orm import Session

from app.models import TicketHistory


def save_ticket_history(
    db: Session,
    input_text: str,
    classification: Any,
) -> TicketHistory:
    executed_action = getattr(classification, "executed_action", None)

    ticket = TicketHistory(
        input_text=input_text,
        category=classification.category,
        priority=classification.priority,
        summary=classification.summary,
        suggested_action=classification.suggested_action,
        source=classification.source,
        executed_action_type=executed_action.action_type if executed_action else None,
        executed_action_status=executed_action.status if executed_action else None,
        executed_action_message=executed_action.message if executed_action else None,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def get_ticket_history(db: Session) -> list[TicketHistory]:
    return (
        db.query(TicketHistory)
        .order_by(TicketHistory.created_at.desc())
        .all()
    )