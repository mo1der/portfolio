from unittest.mock import Mock, patch

import pytest

from app.ai_classifier import classify_text_with_ai


@patch("app.ai_classifier.OPENAI_API_KEY", "fake-api-key")
@patch("app.ai_classifier.OpenAI")
def test_ai_invalid_json_response(mock_openai):
    mock_client = Mock()
    mock_openai.return_value = mock_client

    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                content="TO NIE JEST JSON"
            )
        )
    ]

    mock_client.chat.completions.create.return_value = mock_response

    with pytest.raises(RuntimeError, match="AI zwróciło niepoprawny JSON"):
        classify_text_with_ai("Mam problem z fakturą.")