from app.schemas import Category, ClassificationResponse, Priority


def classify_text(text: str) -> ClassificationResponse:
    lowered_text = text.lower()

    if "hasł" in lowered_text or "login" in lowered_text or "zalog" in lowered_text:
        category = Category.IT_SUPPORT
        priority = Priority.HIGH
        suggested_action = "Przekazać do działu IT."

    elif (
        "faktur" in lowered_text
        or "płatno" in lowered_text
        or "wypłat" in lowered_text
    ):
        category = Category.FINANCE
        priority = Priority.HIGH
        suggested_action = "Przekazać do działu finansów."

    elif "urlop" in lowered_text or "chorob" in lowered_text or "pracownik" in lowered_text:
        category = Category.HR
        priority = Priority.MEDIUM
        suggested_action = "Przekazać do działu HR."

    else:
        category = Category.OTHER
        priority = Priority.LOW
        suggested_action = "Wymaga ręcznej analizy."

    return ClassificationResponse(
        category=category,
        priority=priority,
        summary=text,
        suggested_action=suggested_action,
        source="RULE_BASED",
    )