from unittest.mock import patch

from app.agent_router import route_message
from app.schemas import Category


@patch("app.agent_router.AGENTS")
def test_router_uses_classification_agent(mock_agents):
    def fake_agent(text: str):
        result = type("FakeResponse", (), {})()
        result.category = Category.OTHER
        result.source = "TEST_AGENT"
        return result

    mock_agents.__getitem__.return_value = fake_agent

    result = route_message("Test message")

    assert result.category == Category.OTHER
    assert result.source == "TEST_AGENT"