from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models import (
    TicketHistory,
    TicketStatusHistory,
    TicketComment,
    TicketAssignmentHistory,
)

from app.schemas import TicketStatus


def calculate_sla_due_at(created_at, priority: str):
    if priority == "HIGH":
        return created_at + timedelta(hours=4)

    if priority == "MEDIUM":
        return created_at + timedelta(hours=24)

    if priority == "LOW":
        return created_at + timedelta(hours=72)

    return created_at + timedelta(hours=24)


def calculate_sla_status(ticket):
    if ticket.ticket_status in ["RESOLVED", "CLOSED"]:
        return "COMPLETED"

    if ticket.sla_due_at is None:
        return "UNKNOWN"

    now = datetime.utcnow()

    if now > ticket.sla_due_at:
        return "BREACHED"

    return "ACTIVE"

def determine_default_assignee(category: str, priority: str):
    if category == "FINANCE":
        if priority == "HIGH":
            return "finance_priority_team"

        return "finance_team"

    if category == "IT_SUPPORT":
        if priority == "HIGH":
            return "it_priority_team"

        return "it_support_team"

    if category == "HR":
        if priority == "HIGH":
            return "hr_priority_team"

        return "hr_team"

    if priority == "HIGH":
        return "general_priority_team"

    return "general_team"

def generate_suggested_reply(
    category: str,
    priority: str,
    assigned_to: str | None,
):
    team_text = assigned_to or "odpowiedni zespół"

    if category == "FINANCE":
        if priority == "HIGH":
            return (
                "Dzień dobry, dziękujemy za zgłoszenie. "
                "Sprawa dotycząca finansów została oznaczona jako pilna "
                f"i przekazana do zespołu {team_text}. "
                "Zajmiemy się nią priorytetowo."
            )

        return (
            "Dzień dobry, dziękujemy za zgłoszenie. "
            f"Sprawa dotycząca finansów została przekazana do zespołu {team_text}. "
            "Po weryfikacji wrócimy z odpowiedzią."
        )

    if category == "IT_SUPPORT":
        if priority == "HIGH":
            return (
                "Dzień dobry, dziękujemy za zgłoszenie. "
                "Problem techniczny został oznaczony jako pilny "
                f"i przekazany do zespołu {team_text}. "
                "Prosimy nie zamykać zgłoszenia do czasu rozwiązania problemu."
            )

        return (
            "Dzień dobry, dziękujemy za zgłoszenie. "
            f"Problem techniczny został przekazany do zespołu {team_text}. "
            "Zespół IT przeanalizuje sprawę."
        )

    if category == "HR":
        return (
            "Dzień dobry, dziękujemy za zgłoszenie. "
            f"Sprawa kadrowa została przekazana do zespołu {team_text}. "
            "Po sprawdzeniu informacji wrócimy z odpowiedzią."
        )

    if priority == "HIGH":
        return (
            "Dzień dobry, dziękujemy za zgłoszenie. "
            "Sprawa została oznaczona jako pilna "
            f"i przekazana do zespołu {team_text}. "
            "Zajmiemy się nią możliwie szybko."
        )

    return (
        "Dzień dobry, dziękujemy za zgłoszenie. "
        f"Sprawa została przekazana do zespołu {team_text}. "
        "Wrócimy z odpowiedzią po analizie."
    )

def recalculate_sla_statuses(db):
    tickets = db.query(TicketHistory).all()

    updated_count = 0

    for ticket in tickets:
        old_sla_status = ticket.sla_status
        new_sla_status = calculate_sla_status(ticket)

        if old_sla_status != new_sla_status:
            ticket.sla_status = new_sla_status
            updated_count += 1

    db.commit()

    return {
        "checked_tickets": len(tickets),
        "updated_tickets": updated_count,
    }


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

    category_value = (
        classification.category.value
        if hasattr(classification.category, "value")
        else classification.category
    )

    priority_value = (
        classification.priority.value
        if hasattr(classification.priority, "value")
        else classification.priority
    )

    intent_value = (
        classification.intent.value
        if hasattr(classification.intent, "value")
        else classification.intent
    )

    created_at = datetime.utcnow()
    sla_due_at = calculate_sla_due_at(
        created_at=created_at,
        priority=priority_value,
    )

    assigned_to = determine_default_assignee(
        category=category_value,
        priority=priority_value,
    )

    suggested_reply = generate_suggested_reply(
        category=category_value,
        priority=priority_value,
        assigned_to=assigned_to,
    )

    ticket = TicketHistory(
        input_text=input_text,
        source_channel=source_channel_value,

        category=category_value,
        priority=priority_value,
        intent=intent_value,
        ticket_status=ticket_status_value,
        assigned_to=assigned_to,

        sla_due_at=sla_due_at,
        sla_status="ACTIVE",

        summary=classification.summary,
        suggested_action=classification.suggested_action,
        suggested_reply=suggested_reply,
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
        created_at=created_at,
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
    sla_status=None,
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
        sla_status=sla_status,
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
        "sla_due_at": TicketHistory.sla_due_at,
        "sla_status": TicketHistory.sla_status,
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
    sla_status=None,
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
        sla_status=sla_status,
        search=search,
    )

    return query.count()


def update_ticket_status(db, ticket_id: int, ticket_status: TicketStatus):
    ticket = db.query(TicketHistory).filter(TicketHistory.id == ticket_id).first()

    if ticket is None:
        return None

    ticket.ticket_status = ticket_status.value
    ticket.sla_status = calculate_sla_status(ticket)

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
    sla_status=None,
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

    if sla_status is not None:
        sla_status_value = sla_status.value if hasattr(sla_status, "value") else sla_status

        if sla_status_value == "UNKNOWN":
            query = query.filter(
                or_(
                    TicketHistory.sla_status.is_(None),
                    TicketHistory.sla_status == "",
                    TicketHistory.sla_status == "UNKNOWN",
                )
            )
        else:
            query = query.filter(TicketHistory.sla_status == sla_status_value)

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

    breached_sla_tickets = db.query(TicketHistory).filter(
        TicketHistory.sla_status == "BREACHED"
    ).count()

    active_sla_tickets = db.query(TicketHistory).filter(
        TicketHistory.sla_status == "ACTIVE"
    ).count()

    completed_sla_tickets = db.query(TicketHistory).filter(
        TicketHistory.sla_status == "COMPLETED"
    ).count()

    unknown_sla_tickets = db.query(TicketHistory).filter(
        or_(
            TicketHistory.sla_status.is_(None),
            TicketHistory.sla_status == "",
            TicketHistory.sla_status == "UNKNOWN",
        )
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
        "breached_sla_tickets": breached_sla_tickets,
        "active_sla_tickets": active_sla_tickets,
        "completed_sla_tickets": completed_sla_tickets,
        "unknown_sla_tickets": unknown_sla_tickets,
    }

def get_dashboard_sla_counts(db):
    breached_count = db.query(TicketHistory).filter(
        TicketHistory.sla_status == "BREACHED"
    ).count()

    active_count = db.query(TicketHistory).filter(
        TicketHistory.sla_status == "ACTIVE"
    ).count()

    completed_count = db.query(TicketHistory).filter(
        TicketHistory.sla_status == "COMPLETED"
    ).count()

    unknown_count = db.query(TicketHistory).filter(
        or_(
            TicketHistory.sla_status.is_(None),
            TicketHistory.sla_status == "",
            TicketHistory.sla_status == "UNKNOWN",
        )
    ).count()

    return {
        "items": [
            {
                "name": "BREACHED",
                "count": breached_count,
            },
            {
                "name": "ACTIVE",
                "count": active_count,
            },
            {
                "name": "COMPLETED",
                "count": completed_count,
            },
            {
                "name": "UNKNOWN",
                "count": unknown_count,
            },
        ]
    }

def calculate_percentage(part: int, total: int):
    if total == 0:
        return 0.0

    return round((part / total) * 100, 2)


def get_dashboard_kpis(db):
    total_tickets = db.query(TicketHistory).count()

    open_tickets = db.query(TicketHistory).filter(
        TicketHistory.ticket_status.in_(
            [
                "NEW",
                "IN_PROGRESS",
                "WAITING_FOR_USER",
            ]
        )
    ).count()

    closed_or_resolved_tickets = db.query(TicketHistory).filter(
        TicketHistory.ticket_status.in_(
            [
                "RESOLVED",
                "CLOSED",
            ]
        )
    ).count()

    high_priority_tickets = db.query(TicketHistory).filter(
        TicketHistory.priority == "HIGH"
    ).count()

    breached_sla_tickets = db.query(TicketHistory).filter(
        TicketHistory.sla_status == "BREACHED"
    ).count()

    active_sla_tickets = db.query(TicketHistory).filter(
        TicketHistory.sla_status == "ACTIVE"
    ).count()

    unassigned_tickets = db.query(TicketHistory).filter(
        or_(
            TicketHistory.assigned_to.is_(None),
            TicketHistory.assigned_to == "",
        )
    ).count()

    assigned_tickets = db.query(TicketHistory).filter(
        TicketHistory.assigned_to.isnot(None),
        TicketHistory.assigned_to != "",
    ).count()

    ai_classified_tickets = db.query(TicketHistory).filter(
        TicketHistory.source == "AI"
    ).count()

    rule_based_tickets = db.query(TicketHistory).filter(
        TicketHistory.source == "RULE_BASED"
    ).count()

    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "closed_or_resolved_tickets": closed_or_resolved_tickets,
        "high_priority_tickets": high_priority_tickets,
        "breached_sla_tickets": breached_sla_tickets,
        "active_sla_tickets": active_sla_tickets,
        "unassigned_tickets": unassigned_tickets,
        "assigned_tickets": assigned_tickets,
        "ai_classification_rate": calculate_percentage(
            ai_classified_tickets,
            total_tickets,
        ),
        "rule_based_classification_rate": calculate_percentage(
            rule_based_tickets,
            total_tickets,
        ),
        "auto_assignment_rate": calculate_percentage(
            assigned_tickets,
            total_tickets,
        ),
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
                "created_at": item.changed_at,
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

def get_breached_sla_tickets(db, limit: int = 100):
    safe_limit = max(1, min(limit, 500))

    return (
        db.query(TicketHistory)
        .filter(TicketHistory.sla_status == "BREACHED")
        .order_by(TicketHistory.sla_due_at.asc())
        .limit(safe_limit)
        .all()
    )

def get_sla_tickets(db, status: str | None = None, limit: int = 100):
    safe_limit = max(1, min(limit, 500))

    query = db.query(TicketHistory)

    if status is not None:
        if status == "UNKNOWN":
            query = query.filter(
                or_(
                    TicketHistory.sla_status.is_(None),
                    TicketHistory.sla_status == "",
                    TicketHistory.sla_status == "UNKNOWN",
                )
            )
        else:
            query = query.filter(TicketHistory.sla_status == status)
    else:
        query = query.filter(
            TicketHistory.sla_status.isnot(None),
            TicketHistory.sla_status != "",
        )

    return (
        query
        .order_by(TicketHistory.sla_due_at.asc())
        .limit(safe_limit)
        .all()
    )

def get_due_soon_sla_tickets(db, hours: int = 4, limit: int = 100):
    safe_hours = max(1, min(hours, 168))
    safe_limit = max(1, min(limit, 500))

    now = datetime.utcnow()
    due_until = now + timedelta(hours=safe_hours)

    return (
        db.query(TicketHistory)
        .filter(TicketHistory.sla_status == "ACTIVE")
        .filter(TicketHistory.sla_due_at.isnot(None))
        .filter(TicketHistory.sla_due_at >= now)
        .filter(TicketHistory.sla_due_at <= due_until)
        .order_by(TicketHistory.sla_due_at.asc())
        .limit(safe_limit)
        .all()
    )