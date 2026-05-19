from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import Category, ClassificationResponse, Priority


client = TestClient(app)


@patch("app.process_service.route_message")
def test_process_endpoint_for_finance_high_priority(mock_classify_message):
    mock_classify_message.return_value = ClassificationResponse(
        category=Category.FINANCE,
        priority=Priority.HIGH,
        summary="Problem z fakturą.",
        suggested_action="Przekazać do działu finansów.",
        source="RULE_BASED",
    )

    response = client.post(
        "/process",
        json={
            "text": "Mam pilny problem z fakturą."
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "FINANCE"
    assert data["priority"] == "HIGH"
    assert data["summary"] == "Problem z fakturą."
    assert data["suggested_action"] == "Przekazać do działu finansów."
    assert data["source"] == "RULE_BASED"

    assert data["executed_action"]["action_type"] == "CREATE_FINANCE_TICKET"
    assert data["executed_action"]["target_department"] == "FINANCE"
    assert data["executed_action"]["status"] == "SIMULATED"
    assert "finansów" in data["executed_action"]["message"]