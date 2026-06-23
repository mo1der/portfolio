import re
from difflib import SequenceMatcher

from app.models import TicketHistory


def normalize_text(text: str):
    text = text.lower()
    text = re.sub(r"[^a-ząćęłńóśźż0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def calculate_similarity(first_text: str, second_text: str):
    first_normalized = normalize_text(first_text)
    second_normalized = normalize_text(second_text)

    if not first_normalized or not second_normalized:
        return 0.0

    return round(
        SequenceMatcher(
            None,
            first_normalized,
            second_normalized,
        ).ratio(),
        2,
    )


def find_possible_duplicate_ticket(
    db,
    input_text: str,
    category: str,
    threshold: float = 0.75,
):
    existing_tickets = (
        db.query(TicketHistory)
        .filter(TicketHistory.category == category)
        .order_by(TicketHistory.created_at.desc())
        .limit(50)
        .all()
    )

    best_ticket = None
    best_score = 0.0

    for ticket in existing_tickets:
        score = calculate_similarity(input_text, ticket.input_text)

        if score > best_score:
            best_score = score
            best_ticket = ticket

    if best_ticket is None:
        return {
            "possible_duplicate": False,
            "duplicate_ticket_id": None,
            "duplicate_score": None,
        }

    if best_score < threshold:
        return {
            "possible_duplicate": False,
            "duplicate_ticket_id": None,
            "duplicate_score": best_score,
        }

    return {
        "possible_duplicate": True,
        "duplicate_ticket_id": best_ticket.id,
        "duplicate_score": best_score,
    }