from app.schemas import Category, RouteDecision, ActionType


ROUTING_RULES = [
    {
        "keywords": [
            "faktur",
            "płatność",
            "platnosc",
            "przelew",
            "rachunek",
            "kwota",
            "zapłata",
            "zaplata",
            "koszt",
            "payment",
            "invoice",
        ],
        "category": Category.FINANCE,
        "agent_name": "finance_invoice_agent",
        "default_action_type": ActionType.CREATE_FINANCE_TICKET,
        "reason": "Wiadomość dotyczy faktury, płatności lub rozliczeń.",
    },
    {
        "keywords": [
            "hasł",
            "haslo",
            "logowan",
            "login",
            "zalog",
            "dostęp",
            "dostep",
            "komputer",
            "drukarka",
            "vpn",
            "aplikacja",
            "program",
            "awaria",
        ],
        "category": Category.IT_SUPPORT,
        "agent_name": "it_access_agent",
        "default_action_type": ActionType.CREATE_IT_SUPPORT_TICKET,
        "reason": "Wiadomość dotyczy problemów IT, dostępu, logowania lub sprzętu.",
    },
    {
        "keywords": [
            "urlop",
            "zwoln",
            "l4",
            "chorobowe",
            "wynagrodzen",
            "pensja",
            "wypłata",
            "wyplata",
            "wniosek",
            "kadry",
            "grafik",
        ],
        "category": Category.HR,
        "agent_name": "hr_leave_agent",
        "default_action_type": ActionType.CREATE_HR_TICKET,
        "reason": "Wiadomość dotyczy HR, urlopu, wynagrodzenia lub spraw pracowniczych.",
    },
]


def route_message(category: Category, text: str) -> RouteDecision:
    """
    Zwraca RouteDecision na podstawie kategorii i słów kluczowych.
    Jeśli kategoria jest znana, ale tekst nie pasuje do szczegółowej reguły,
    kieruje do domyślnego agenta dla tej kategorii.
    """
    text_lower = text.lower()

    for rule in ROUTING_RULES:
        if rule["category"] == category:
            if any(keyword in text_lower for keyword in rule["keywords"]):
                return RouteDecision(
                    agent_name=rule["agent_name"],
                    department=rule["category"],
                    reason=rule["reason"],
                    default_action_type=rule["default_action_type"],
                )

    if category == Category.FINANCE:
        return RouteDecision(
            agent_name="finance_invoice_agent",
            department=Category.FINANCE,
            reason="Kategoria FINANCE została rozpoznana, ale brak szczegółowego dopasowania słów kluczowych.",
            default_action_type=ActionType.CREATE_FINANCE_TICKET,
        )

    if category == Category.IT_SUPPORT:
        return RouteDecision(
            agent_name="it_access_agent",
            department=Category.IT_SUPPORT,
            reason="Kategoria IT_SUPPORT została rozpoznana, ale brak szczegółowego dopasowania słów kluczowych.",
            default_action_type=ActionType.CREATE_IT_SUPPORT_TICKET,
        )

    if category == Category.HR:
        return RouteDecision(
            agent_name="hr_leave_agent",
            department=Category.HR,
            reason="Kategoria HR została rozpoznana, ale brak szczegółowego dopasowania słów kluczowych.",
            default_action_type=ActionType.CREATE_HR_TICKET,
        )

    return RouteDecision(
        agent_name="general_agent",
        department=category,
        reason="Brak dopasowania do reguł. Kierowane do agenta ogólnego.",
        default_action_type=ActionType.SEND_TO_GENERAL_QUEUE,
    )