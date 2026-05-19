from unittest.mock import patch

from app.process_service import process_message
from app.schemas import (
    ActionStatus,
    ActionType,
    Category,
    ClassificationRequest,
    ClassificationResponse,
    Priority,
)

@patch("app.process_service.route_message")
def test_process_message_for_finance_high_priority(mock_route_message):
    mock_route_message.return_value = ClassificationResponse(
        category=Category.FINANCE,
        priority=Priority.HIGH,
        summary="Problem z fakturą.",
        suggested_action="Przekazać do działu finansów.",
        source="RULE_BASED",
    )

    request = ClassificationRequest(text="Mam problem z fakturą.")

    result = process_message(request)

    assert result.category == Category.FINANCE
    assert result.priority == Priority.HIGH
    assert result.summary == "Problem z fakturą."
    assert result.suggested_action == "Przekazać do działu finansów."
    assert result.source == "RULE_BASED"

    assert result.executed_action.action_type == ActionType.CREATE_FINANCE_TICKET
    assert result.executed_action.target_department == Category.FINANCE
    assert result.executed_action.status == ActionStatus.SIMULATED
    assert "finansów" in result.executed_action.message