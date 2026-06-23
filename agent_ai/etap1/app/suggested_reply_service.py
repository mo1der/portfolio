import os


def generate_rule_based_suggested_reply(
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


def generate_ai_suggested_reply(
    input_text: str,
    category: str,
    priority: str,
    assigned_to: str | None,
):
    ai_enabled = os.getenv("AI_ENABLED", "false").lower() == "true"

    if not ai_enabled:
        return None

    # Tu w kolejnym kroku podepniemy realne OpenAI.
    # Na razie funkcja jest przygotowana pod AI i daje fallback.
    return None


def generate_suggested_reply_with_source(
    input_text: str,
    category: str,
    priority: str,
    assigned_to: str | None,
):
    ai_reply = generate_ai_suggested_reply(
        input_text=input_text,
        category=category,
        priority=priority,
        assigned_to=assigned_to,
    )

    if ai_reply:
        return {
            "suggested_reply": ai_reply,
            "suggested_reply_source": "AI",
        }

    rule_based_reply = generate_rule_based_suggested_reply(
        category=category,
        priority=priority,
        assigned_to=assigned_to,
    )

    return {
        "suggested_reply": rule_based_reply,
        "suggested_reply_source": "RULE_BASED",
    }