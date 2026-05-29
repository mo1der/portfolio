from app.schemas import TicketStatus


ALLOWED_STATUS_TRANSITIONS = {
    TicketStatus.NEW: {
        TicketStatus.IN_PROGRESS,
    },
    TicketStatus.IN_PROGRESS: {
        TicketStatus.WAITING_FOR_USER,
        TicketStatus.RESOLVED,
    },
    TicketStatus.WAITING_FOR_USER: {
        TicketStatus.IN_PROGRESS,
        TicketStatus.RESOLVED,
    },
    TicketStatus.RESOLVED: {
        TicketStatus.CLOSED,
    },
    TicketStatus.CLOSED: set(),
}


def normalize_ticket_status(status) -> TicketStatus:
    if isinstance(status, TicketStatus):
        return status

    return TicketStatus(status)


def is_status_transition_allowed(current_status, new_status) -> bool:
    current_status = normalize_ticket_status(current_status)
    new_status = normalize_ticket_status(new_status)

    if current_status == new_status:
        return True

    allowed_next_statuses = ALLOWED_STATUS_TRANSITIONS[current_status]

    return new_status in allowed_next_statuses