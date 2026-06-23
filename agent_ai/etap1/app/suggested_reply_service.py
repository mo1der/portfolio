from openai import OpenAI

from app.core.settings import settings


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
    if not settings.ai_enabled:
        return None

    if not settings.openai_api_key:
        return None

    try:
        client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=10,
        )

        team_text = assigned_to or "odpowiedni zespół"

        prompt = f"""
Napisz krótką, profesjonalną propozycję odpowiedzi do klienta po polsku.

Zasady:
- maksymalnie 3 zdania,
- ton spokojny i profesjonalny,
- nie obiecuj rozwiązania problemu,
- nie podawaj niepewnych informacji,
- uwzględnij kategorię, priorytet i zespół,
- odpowiedź ma być gotowa do wysłania przez konsultanta.

Dane zgłoszenia:
Treść klienta: {input_text}
Kategoria: {category}
Priorytet: {priority}
Zespół: {team_text}
""".strip()

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Jesteś asystentem działu obsługi klienta. "
                        "Tworzysz krótkie, bezpieczne i profesjonalne odpowiedzi."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_tokens=150,
        )

        reply = response.choices[0].message.content

        if reply is None:
            return None

        reply = reply.strip()

        if not reply:
            return None

        return reply

    except Exception:
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