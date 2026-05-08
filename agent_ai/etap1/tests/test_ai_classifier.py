from unittest.mock import patch

from app.ai_classifier import classify_text_with_ai
from app.schemas import Category, Priority


class MockMessage:
    content = """
    {
        "category": "FINANCE",
        "priority": "HIGH",
        "summary": "Klient zgłasza problem z fakturą.",
        "suggested_action": "Przekazać do działu finansów."
    }
    """


class MockChoice:
    message = MockMessage()


class MockResponse:
    choices = [MockChoice()]


@patch("app.ai_classifier.client.chat.completions.create")
def test_ai_classifier(mock_create):
    mock_create.return_value = MockResponse()

    result = classify_text_with_ai(
        "Nie dostałem faktury."
    )

    assert result.category == Category.FINANCE
    assert result.priority == Priority.HIGH
    assert result.source == "AI"