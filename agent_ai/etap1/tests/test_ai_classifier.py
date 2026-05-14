from unittest.mock import Mock, patch

from app.ai_classifier import classify_text_with_ai


@patch("app.ai_classifier.OPENAI_API_KEY", "fake-api-key")
@patch("app.ai_classifier.OpenAI")
def test_ai_classifier(mock_openai):
    mock_client = Mock()
    mock_openai.return_value = mock_client

    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                content="""
                {
                    "category": "FINANCE",
                    "priority": "HIGH",
                    "summary": "Klient zgłasza problem z fakturą.",
                    "suggested_action": "Przekazać do działu finansów."
                }
                """
            )
        )
    ]

    mock_client.chat.completions.create.return_value = mock_response

    result = classify_text_with_ai("Nie dostałem faktury.")

    assert result["category"] == "FINANCE"
    assert result["priority"] == "HIGH"
    assert result["summary"] == "Klient zgłasza problem z fakturą."
    assert result["suggested_action"] == "Przekazać do działu finansów."

    mock_client.chat.completions.create.assert_called_once()