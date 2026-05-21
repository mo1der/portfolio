from sqlalchemy.orm import Session
from app.models import TicketHistory

def save_ticket_history(db: Session, input_text: str, classification):
    """
    Zapisuje zgłoszenie do bazy.
    Obsługuje ClassificationResponse lub ProcessResponse.
    """
    executed = getattr(classification, "executed_action", None)
    route = getattr(classification, "route", None)

    ticket = TicketHistory(
        input_text=input_text,
        category=classification.category.value if hasattr(classification.category, "value") else classification.category,
        priority=classification.priority.value if hasattr(classification.priority, "value") else classification.priority,
        summary=classification.summary,
        suggested_action=classification.suggested_action,
        source=classification.source,

        executed_action_type=executed.action_type.value if executed and hasattr(executed.action_type, "value") else (executed.action_type if executed else None),
        executed_action_status=executed.status.value if executed and hasattr(executed.status, "value") else (executed.status if executed else None),
        executed_action_message=executed.message if executed else None,

        route_agent_name=route.agent_name if route else None,
        route_department=route.department.value if route and hasattr(route.department, "value") else (route.department if route else None),
        route_reason=route.reason if route else None,
        route_action_type=route.action_type.value if route and hasattr(route.action_type, "value") else (route.action_type if route else None)
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