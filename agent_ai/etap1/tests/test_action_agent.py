from app.action_agent import choose_action
from app.schemas import ActionType, Category, ClassificationResponse, Priority


def test_choose_action_for_low_priority():
    classification = ClassificationResponse(
        category=Category.FINANCE,
        priority=Priority.LOW,
        summary="Pytanie o fakturę.",
        suggested_action="Obsłużyć w standardowym trybie.",
        source="RULE_BASED",
    )

    result = choose_action(classification)

    assert result == ActionType.MARK_AS_LOW_PRIORITY


def test_choose_action_for_finance():
    classification = ClassificationResponse(
        category=Category.FINANCE,
        priority=Priority.HIGH,
        summary="Problem z fakturą.",
        suggested_action="Przekazać do działu finansów.",
        source="RULE_BASED",
    )

    result = choose_action(classification)

    assert result == ActionType.CREATE_FINANCE_TICKET


def test_choose_action_for_it_support():
    classification = ClassificationResponse(
        category=Category.IT_SUPPORT,
        priority=Priority.HIGH,
        summary="Problem z logowaniem.",
        suggested_action="Przekazać do działu IT.",
        source="RULE_BASED",
    )

    result = choose_action(classification)

    assert result == ActionType.CREATE_IT_SUPPORT_TICKET


def test_choose_action_for_hr():
    classification = ClassificationResponse(
        category=Category.HR,
        priority=Priority.MEDIUM,
        summary="Pytanie o urlop.",
        suggested_action="Przekazać do działu HR.",
        source="RULE_BASED",
    )

    result = choose_action(classification)

    assert result == ActionType.CREATE_HR_TICKET

def test_choose_action_for_other_high_priority():
    classification = ClassificationResponse(
        category=Category.OTHER,
        priority=Priority.HIGH,
        summary="Pilna sprawa ogólna.",
        suggested_action="Przekazać do osoby odpowiedzialnej.",
        source="RULE_BASED",
    )

    result = choose_action(classification)

    assert result == ActionType.ESCALATE_TO_MANAGER


def test_choose_action_for_other_medium_priority():
    classification = ClassificationResponse(
        category=Category.OTHER,
        priority=Priority.MEDIUM,
        summary="Zwykła sprawa ogólna.",
        suggested_action="Przekazać do kolejki ogólnej.",
        source="RULE_BASED",
    )

    result = choose_action(classification)

    assert result == ActionType.SEND_TO_GENERAL_QUEUE