from sqlalchemy.orm import Session

from app.models import TicketHistory
from app.schemas import ClassificationResponse


def save_ticket_history(
    db: Session,
    input_text: str,
    classification: ClassificationResponse,
) -> TicketHistory:
    ticket = TicketHistory(
        input_text=input_text,
        category=classification.category,
        priority=classification.priority,
        summary=classification.summary,
        suggested_action=classification.suggested_action,
        source=classification.source,
        executed_action_type=None,
        executed_action_status=None,
        executed_action_message=None,
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