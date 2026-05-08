from unittest.mock import patch

from app.classification_service import classify_message
from app.schemas import Category


@patch("app.classification_service.classify_text_with_ai")
def test_service_uses_ai_when_ai_works(mock_ai):
    mock_ai.return_value.category = Category.FINANCE
    mock_ai.return_value.source = "AI"

    result = classify_message("Mam problem z fakturą.")

    assert result.category == Category.FINANCE
    assert result.source == "AI"


@patch("app.classification_service.classify_text_with_ai")
def test_service_uses_fallback_when_ai_fails(mock_ai):
    mock_ai.side_effect = Exception("AI failed")

    result = classify_message("Mam problem z fakturą.")

    assert result.category == Category.FINANCE
    assert result.source == "RULE_BASED"