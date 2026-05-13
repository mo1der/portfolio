from unittest.mock import patch

from app.classification_service import classify_message
from app.schemas import ClassificationResponse


@patch("app.classification_service.classify_text_with_ai")
def test_classify_message_uses_ai_when_ai_succeeds(mock_ai):
    mock_ai.return_value = ClassificationResponse(
        category="IT_SUPPORT",
        priority="HIGH",
        summary="Problem z laptopem",
        suggested_action="Przekazać do IT",
        source="AI",
    )

    result = classify_message("Laptop nie działa")

    assert result.category == "IT_SUPPORT"
    assert result.source == "AI"


@patch("app.classification_service.classify_text_with_ai")
@patch("app.classification_service.classify_text")
def test_classify_message_uses_fallback_when_ai_fails(mock_fallback, mock_ai):
    mock_ai.side_effect = Exception("AI error")
    mock_fallback.return_value = ClassificationResponse(
        category="OTHER",
        priority="LOW",
        summary="Fallback summary",
        suggested_action="Review manually",
        source="RULE_BASED",
    )

    result = classify_message("Jakiś tekst")

    assert result.source == "RULE_BASED"
    mock_fallback.assert_called_once_with("Jakiś tekst")


@patch("app.classification_service.settings")
@patch("app.classification_service.classify_text_with_ai")
@patch("app.classification_service.classify_text")
def test_classify_message_uses_fallback_when_ai_disabled(
    mock_fallback,
    mock_ai,
    mock_settings,
):
    mock_settings.ai_enabled = False
    mock_fallback.return_value = ClassificationResponse(
        category="FINANCE",
        priority="LOW",
        summary="Problem z fakturą",
        suggested_action="Przekazać do działu finansów",
        source="RULE_BASED",
    )

    result = classify_message("Problem z fakturą")

    assert result.source == "RULE_BASED"
    assert result.category == "FINANCE"
    mock_ai.assert_not_called()
    mock_fallback.assert_called_once_with("Problem z fakturą")