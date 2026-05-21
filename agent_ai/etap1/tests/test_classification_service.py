import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.database import engine

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


@pytest.mark.parametrize(
    "text,expected_agent",
    [
        ("Mam problem z fakturą", "finance_invoice_agent"),
        ("Nie mogę zalogować się do VPN", "it_access_agent"),
        ("Chcę złożyć wniosek urlopowy", "hr_leave_agent"),
        ("Pytanie ogólne do systemu", "general_agent"),
    ],
)
def test_classify_routing(text, expected_agent):
    input_text = f"TEST_{text}"

    try:
        response = client.post("/classify", json={"text": input_text})

        assert response.status_code == 200

        data = response.json()

        assert "route" in data
        assert data["route"]["agent_name"] == expected_agent
        assert data["summary"] == input_text

    finally:
        delete_test_tickets()