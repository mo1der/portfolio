from unittest.mock import patch

import pytest

from app.ai_classifier import classify_text_with_ai
from app.exceptions import AIResponseError


class MockMessage:
    content = "TO NIE JEST JSON"


class MockChoice:
    message = MockMessage()


class MockResponse:
    choices = [MockChoice()]


@patch("app.ai_classifier.client.chat.completions.create")
def test_ai_invalid_json_response(mock_create):
    mock_create.return_value = MockResponse()

    with pytest.raises(AIResponseError):
        classify_text_with_ai(
            "Mam problem z fakturą."
        )