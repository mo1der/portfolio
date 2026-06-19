from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models import (
    TicketHistory,
    TicketStatusHistory,
    TicketComment,
    TicketAssignmentHistory,
    )

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

def get_ticket_history(
    db,
    ticket_status=None,
    category=None,
    priority=None,
    intent=None,
    source_channel=None,
    assigned_to=None,
    search=None,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    query = build_ticket_history_query(
        db=db,
        ticket_status=ticket_status,
        category=category,
        priority=priority,
        intent=intent,
        source_channel=source_channel,
        assigned_to=assigned_to,
        search=search,
    )

    allowed_sort_fields = {
        "id": TicketHistory.id,
        "created_at": TicketHistory.created_at,
        "category": TicketHistory.category,
        "priority": TicketHistory.priority,
        "ticket_status": TicketHistory.ticket_status,
        "source_channel": TicketHistory.source_channel,
        "assigned_to": TicketHistory.assigned_to,
    }

    sort_column = allowed_sort_fields.get(sort_by, TicketHistory.created_at)

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    return query.offset(offset).limit(limit).all()

def count_ticket_history(
    db,
    ticket_status=None,
    category=None,
    priority=None,
    intent=None,
    source_channel=None,
    assigned_to=None,
    search=None,
):
    query = build_ticket_history_query(
        db=db,
        ticket_status=ticket_status,
        category=category,
        priority=priority,
        intent=intent,
        source_channel=source_channel,
        assigned_to=assigned_to,
        search=search,
    )

    return query.count()

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
    changed_by: str | None = None,
    note: str | None = None,
):
    history = TicketStatusHistory(
        ticket_id=ticket_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        note=note,
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history

def get_ticket_status_history(db, ticket_id: int):
    return (
        db.query(TicketStatusHistory)
        .filter(TicketStatusHistory.ticket_id == ticket_id)
        .order_by(TicketStatusHistory.changed_at.asc())
        .all()
    )

def create_ticket_comment(
    db,
    ticket_id: int,
    comment_text: str,
    author: str = "SYSTEM",
):
    comment = TicketComment(
        ticket_id=ticket_id,
        comment_text=comment_text,
        author=author,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


def get_ticket_comments(db, ticket_id: int):
    return (
        db.query(TicketComment)
        .filter(TicketComment.ticket_id == ticket_id)
        .order_by(TicketComment.created_at.asc())
        .all()
    )

def assign_ticket(
    db,
    ticket_id: int,
    assigned_to: str | None,
    changed_by: str | None = None,
    note: str | None = None,
):
    ticket = db.query(TicketHistory).filter(TicketHistory.id == ticket_id).first()

    if ticket is None:
        return None

    old_assigned_to = ticket.assigned_to

    ticket.assigned_to = assigned_to

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    create_ticket_assignment_history(
        db=db,
        ticket_id=ticket.id,
        old_assigned_to=old_assigned_to,
        new_assigned_to=assigned_to,
        changed_by=changed_by,
        note=note,
    )

    return ticket


def build_ticket_history_query(
    db,
    ticket_status=None,
    category=None,
    priority=None,
    intent=None,
    source_channel=None,
    assigned_to=None,
    search=None,
):
    query = db.query(TicketHistory)

    if ticket_status is not None:
        status_value = ticket_status.value if hasattr(ticket_status, "value") else ticket_status
        query = query.filter(TicketHistory.ticket_status == status_value)

    if category is not None:
        category_value = category.value if hasattr(category, "value") else category
        query = query.filter(TicketHistory.category == category_value)

    if priority is not None:
        priority_value = priority.value if hasattr(priority, "value") else priority
        query = query.filter(TicketHistory.priority == priority_value)

    if intent is not None:
        intent_value = intent.value if hasattr(intent, "value") else intent
        query = query.filter(TicketHistory.intent == intent_value)

    if source_channel is not None:
        source_channel_value = (
            source_channel.value if hasattr(source_channel, "value") else source_channel
        )
        query = query.filter(TicketHistory.source_channel == source_channel_value)

    if assigned_to is not None:
        query = query.filter(TicketHistory.assigned_to == assigned_to)

    if search is not None and search.strip():
        search_pattern = f"%{search.strip()}%"

        query = query.filter(
            or_(
                TicketHistory.input_text.ilike(search_pattern),
                TicketHistory.summary.ilike(search_pattern),
                TicketHistory.suggested_action.ilike(search_pattern),
                TicketHistory.executed_action_message.ilike(search_pattern),
                TicketHistory.route_reason.ilike(search_pattern),
            )
        )

    return query

def get_dashboard_summary(db):
    total_tickets = db.query(TicketHistory).count()

    new_tickets = db.query(TicketHistory).filter(
        TicketHistory.ticket_status == "NEW"
    ).count()

    in_progress_tickets = db.query(TicketHistory).filter(
        TicketHistory.ticket_status == "IN_PROGRESS"
    ).count()

    waiting_for_user_tickets = db.query(TicketHistory).filter(
        TicketHistory.ticket_status == "WAITING_FOR_USER"
    ).count()

    resolved_tickets = db.query(TicketHistory).filter(
        TicketHistory.ticket_status == "RESOLVED"
    ).count()

    closed_tickets = db.query(TicketHistory).filter(
        TicketHistory.ticket_status == "CLOSED"
    ).count()

    high_priority_tickets = db.query(TicketHistory).filter(
        TicketHistory.priority == "HIGH"
    ).count()

    unassigned_tickets = db.query(TicketHistory).filter(
        or_(
            TicketHistory.assigned_to.is_(None),
            TicketHistory.assigned_to == "",
        )
    ).count()

    ai_classified_tickets = db.query(TicketHistory).filter(
        TicketHistory.source == "AI"
    ).count()

    rule_based_tickets = db.query(TicketHistory).filter(
        TicketHistory.source == "RULE_BASED"
    ).count()

    return {
        "total_tickets": total_tickets,
        "new_tickets": new_tickets,
        "in_progress_tickets": in_progress_tickets,
        "waiting_for_user_tickets": waiting_for_user_tickets,
        "resolved_tickets": resolved_tickets,
        "closed_tickets": closed_tickets,
        "high_priority_tickets": high_priority_tickets,
        "unassigned_tickets": unassigned_tickets,
        "ai_classified_tickets": ai_classified_tickets,
        "rule_based_tickets": rule_based_tickets,
    }

def get_dashboard_counts_by_field(db, field_name: str):
    allowed_fields = {
        "ticket_status": TicketHistory.ticket_status,
        "category": TicketHistory.category,
        "priority": TicketHistory.priority,
        "source": TicketHistory.source,
        "assigned_to": TicketHistory.assigned_to,
    }

    field = allowed_fields.get(field_name)

    if field is None:
        return []

    results = (
        db.query(field, func.count(TicketHistory.id))
        .group_by(field)
        .order_by(func.count(TicketHistory.id).desc())
        .all()
    )

    items = []

    for name, count in results:
        if name is None or name == "":
            display_name = "UNASSIGNED"
        else:
            display_name = str(name)

        items.append(
            {
                "name": display_name,
                "count": count,
            }
        )

    return {
        "items": items
    }

def get_recent_tickets(db, limit: int = 5):
    safe_limit = max(1, min(limit, 20))

    return (
        db.query(TicketHistory)
        .order_by(TicketHistory.created_at.desc())
        .limit(safe_limit)
        .all()
    )

def get_urgent_tickets(db, limit: int = 5):
    safe_limit = max(1, min(limit, 20))

    return (
        db.query(TicketHistory)
        .filter(TicketHistory.priority == "HIGH")
        .filter(TicketHistory.ticket_status != "CLOSED")
        .order_by(TicketHistory.created_at.desc())
        .limit(safe_limit)
        .all()
    )

def get_unassigned_tickets(db, limit: int = 5):
    safe_limit = max(1, min(limit, 20))

    return (
        db.query(TicketHistory)
        .filter(
            or_(
                TicketHistory.assigned_to.is_(None),
                TicketHistory.assigned_to == "",
            )
        )
        .filter(TicketHistory.ticket_status != "CLOSED")
        .order_by(TicketHistory.created_at.desc())
        .limit(safe_limit)
        .all()
    )

def get_tickets_by_day(db):
    results = (
        db.query(
            func.date(TicketHistory.created_at),
            func.count(TicketHistory.id),
        )
        .group_by(func.date(TicketHistory.created_at))
        .order_by(func.date(TicketHistory.created_at).asc())
        .all()
    )

    items = []

    for date_value, count in results:
        items.append(
            {
                "date": str(date_value),
                "count": count,
            }
        )

    return {
        "items": items
    }

def create_ticket_assignment_history(
    db,
    ticket_id: int,
    old_assigned_to: str | None,
    new_assigned_to: str | None,
    changed_by: str | None = None,
    note: str | None = None,
):
    history = TicketAssignmentHistory(
        ticket_id=ticket_id,
        old_assigned_to=old_assigned_to,
        new_assigned_to=new_assigned_to,
        changed_by=changed_by,
        note=note,
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history


def get_ticket_assignment_history(db, ticket_id: int):
    return (
        db.query(TicketAssignmentHistory)
        .filter(TicketAssignmentHistory.ticket_id == ticket_id)
        .order_by(TicketAssignmentHistory.created_at.asc())
        .all()
    )

def get_ticket_timeline(db, ticket_id: int):
    ticket = db.query(TicketHistory).filter(TicketHistory.id == ticket_id).first()

    if ticket is None:
        return None

    timeline_items = []

    timeline_items.append(
        {
            "event_type": "CREATED",
            "title": "Ticket created",
            "description": ticket.input_text,
            "author": ticket.source_channel,
            "created_at": ticket.created_at,
        }
    )

    status_history = get_ticket_status_history(db=db, ticket_id=ticket_id)

    for item in status_history:
        timeline_items.append(
            {
                "event_type": "STATUS_CHANGED",
                "title": f"Status changed: {item.old_status} -> {item.new_status}",
                "description": item.note,
                "author": item.changed_by,
                "created_at": item.created_at,
            }
        )

    assignment_history = get_ticket_assignment_history(db=db, ticket_id=ticket_id)

    for item in assignment_history:
        timeline_items.append(
            {
                "event_type": "ASSIGNED",
                "title": f"Assigned: {item.old_assigned_to} -> {item.new_assigned_to}",
                "description": item.note,
                "author": item.changed_by,
                "created_at": item.created_at,
            }
        )

    comments = get_ticket_comments(db=db, ticket_id=ticket_id)

    for item in comments:
        timeline_items.append(
            {
                "event_type": "COMMENT_ADDED",
                "title": "Comment added",
                "description": item.comment_text,
                "author": item.author,
                "created_at": item.created_at,
            }
        )

    timeline_items.sort(key=lambda item: item["created_at"])

    return {
        "items": timeline_items
    }