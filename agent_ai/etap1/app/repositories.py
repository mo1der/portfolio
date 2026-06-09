from sqlalchemy.orm import Session

from app.models import TicketHistory, TicketStatusHistory
from app.schemas import TicketStatus

def save_ticket_history(db: Session, input_text: str, classification):
    """
    Zapisuje zgłoszenie do bazy.
    Obsługuje ClassificationResponse lub ProcessResponse.
    """
    executed = getattr(classification, "executed_action", None)
    route = getattr(classification, "route", None)

    source_channel = getattr(classification, "source_channel", "API")
    source_channel_value = (
        source_channel.value
        if hasattr(source_channel, "value")
        else source_channel
    )

    ticket_status = getattr(classification, "ticket_status", "NEW")
    ticket_status_value = (
        ticket_status.value
        if hasattr(ticket_status, "value")
        else ticket_status
    )

    ticket = TicketHistory(
        input_text=input_text,
        source_channel=source_channel_value,

        category=(
            classification.category.value
            if hasattr(classification.category, "value")
            else classification.category
        ),
        priority=(
            classification.priority.value
            if hasattr(classification.priority, "value")
            else classification.priority
        ),
        intent=(
            classification.intent.value
            if hasattr(classification.intent, "value")
            else classification.intent
        ),
        ticket_status=ticket_status_value,

        summary=classification.summary,
        suggested_action=classification.suggested_action,
        source=classification.source,

        executed_action_type=(
            executed.action_type.value
            if executed and hasattr(executed.action_type, "value")
            else (executed.action_type if executed else None)
        ),
        executed_action_status=(
            executed.status.value
            if executed and hasattr(executed.status, "value")
            else (executed.status if executed else None)
        ),
        executed_action_message=executed.message if executed else None,

        route_agent_name=route.agent_name if route else None,
        route_department=(
            route.department.value
            if route and hasattr(route.department, "value")
            else (route.department if route else None)
        ),
        route_reason=route.reason if route else None,
        route_action_type=(
            route.default_action_type.value
            if route and hasattr(route.default_action_type, "value")
            else (route.default_action_type if route else None)
        ),
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket



def get_ticket_history(db: Session):
    """
    Pobiera wszystkie zgłoszenia z bazy, posortowane od najnowszych.
    """
    return db.query(TicketHistory).order_by(TicketHistory.id.desc()).all()

def update_ticket_status(db, ticket_id: int, ticket_status: TicketStatus):
    ticket = db.query(TicketHistory).filter(TicketHistory.id == ticket_id).first()

    if ticket is None:
        return None

    ticket.ticket_status = ticket_status.value
    db.commit()
    db.refresh(ticket)

    return ticket

def get_ticket_by_id(db, ticket_id: int):
    return db.query(TicketHistory).filter(TicketHistory.id == ticket_id).first()

def save_ticket_status_history(
    db,
    ticket_id: int,
    old_status: str,
    new_status: str,
    changed_by: str = "SYSTEM",
):
    history_entry = TicketStatusHistory(
        ticket_id=ticket_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
    )

    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)

    return history_entry


def get_ticket_status_history(db, ticket_id: int):
    return (
        db.query(TicketStatusHistory)
        .filter(TicketStatusHistory.ticket_id == ticket_id)
        .order_by(TicketStatusHistory.changed_at.asc())
        .all()
    )