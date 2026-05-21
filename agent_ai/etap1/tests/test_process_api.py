from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.database import engine
from app.schemas import Category, Priority, ClassificationResponse

client = TestClient(app)


def delete_test_tickets():
    """
    Usuwa tylko rekordy testowe.
    Nie rusza prawdziwej historii zgłoszeń.
    """
    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM ticket_history WHERE input_text LIKE 'TEST_%'")
        )


@patch("app.process_service.route_message")
def test_process_endpoint_for_finance_high_priority(mock_route):
    input_text = "TEST_Mam pilny problem z fakturą."

    # mockujemy routing
    mock_route.return_value = ClassificationResponse(
        category=Category.FINANCE,
        priority=Priority.HIGH,
        summary=input_text,
        suggested_action="Przekazać do działu finansów.",
        source="RULE_BASED",
    )

    try:
        response = client.post("/process", json={"text": input_text})

        assert response.status_code == 200

        data = response.json()

        assert data["category"] == Category.FINANCE
        assert data["priority"] == Priority.HIGH
        assert data["summary"] == input_text

    finally:
        delete_test_tickets()