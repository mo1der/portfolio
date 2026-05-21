from app.schemas import Category, RouteDecision, ActionType

ROUTING_RULES = [
    {
        "keywords": ["faktur", "płatność", "przelew", "rachunek"],
        "category": Category.FINANCE,
        "agent_name": "finance_invoice_agent",
        "action_type": ActionType.CREATE_FINANCE_TICKET,  # pozostaje bez zmian
        "reason": "Wiadomość dotyczy faktury lub płatności."
    },
    {
        "keywords": ["hasł", "logowan", "komputer", "drukarka", "vpn"],
        "category": Category.IT_SUPPORT,
        "agent_name": "it_access_agent",
        "action_type": ActionType.CREATE_IT_SUPPORT_TICKET,  # zmienione
        "reason": "Wiadomość dotyczy problemów IT."
    },
    {
        "keywords": ["urlop", "zwoln", "wynagrodzen", "wniosek"],
        "category": Category.HR,
        "agent_name": "hr_leave_agent",
        "action_type": ActionType.CREATE_HR_TICKET,  # zmienione
        "reason": "Wiadomość dotyczy HR, np. urlopu lub wynagrodzenia."
    }
]

def route_message(category: Category, text: str) -> RouteDecision:
    """
    Zwraca RouteDecision na podstawie kategorii i słów kluczowych.
    Fallback do general_agent jeśli nic nie pasuje.
    """
    text_lower = text.lower()
    for rule in ROUTING_RULES:
        if rule["category"] == category:
            if any(keyword in text_lower for keyword in rule["keywords"]):
                return RouteDecision(
                    agent_name=rule["agent_name"],
                    department=rule["category"],
                    reason=rule["reason"],
                    action_type=rule["action_type"]
                )

    # fallback
    return RouteDecision(
        agent_name="general_agent",
        department=category,
        reason="Brak dopasowania do reguł. Kierowane do agenta ogólnego.",
        action_type=ActionType.SEND_TO_GENERAL_QUEUE
    )