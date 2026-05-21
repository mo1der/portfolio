from app.schemas import Category, Priority, ActionType

def classify_text_rule_based(text: str) -> dict:
    """
    Rule-based classifier dla Etapu 5.
    Zwraca dict z keys: category, priority, summary, suggested_action, source, action_type
    """
    text_lower = text.lower()

    # FINANCE
    if any(word in text_lower for word in ["faktur", "płatność", "przelew"]):
        category = Category.FINANCE
        priority = Priority.HIGH
        suggested_action = "Przekazać do działu finansów."
        action_type = ActionType.CREATE_FINANCE_TICKET
    # IT_SUPPORT
    elif any(word in text_lower for word in ["hasł", "logowan", "zalog", "komputer", "drukarka", "vpn"]):
        category = Category.IT_SUPPORT
        priority = Priority.HIGH
        suggested_action = "Przekazać do działu IT."
        action_type = ActionType.CREATE_IT_SUPPORT_TICKET
    # HR
    elif any(word in text_lower for word in ["urlop", "zwoln", "wynagrodzen", "wniosek"]):
        category = Category.HR
        priority = Priority.MEDIUM
        suggested_action = "Przekazać do działu HR."
        action_type = ActionType.CREATE_HR_TICKET
    # OTHER
    else:
        category = Category.OTHER
        priority = Priority.LOW
        suggested_action = "Przekazać do ogólnej kolejki."
        action_type = ActionType.SEND_TO_GENERAL_QUEUE

    return {
        "category": category,
        "priority": priority,
        "summary": text,  # dokładny tekst użytkownika
        "suggested_action": suggested_action,
        "source": "RULE_BASED",
        "action_type": action_type
    }