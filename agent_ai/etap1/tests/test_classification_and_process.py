import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.schemas import Category
from app.database import engine

client = TestClient(app)


def delete_test_tickets():
    """
    Usuwa tylko rekordy testowe, które mają prefix 'TEST_' w input_text.
    """
    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM ticket_history WHERE input_text LIKE 'TEST_%'")
        )


@pytest.mark.parametrize(
    "text,expected_category,expected_agent",
    [
        ("Mam pilny problem z fakturą za ostatni miesiąc.", Category.FINANCE, "finance_invoice_agent"),
        ("Nie mogę zalogować się do VPN.", Category.IT_SUPPORT, "it_access_agent"),
        ("Chcę zgłosić urlop na przyszły tydzień.", Category.HR, "hr_leave_agent"),
        ("Pytanie ogólne do systemu.", Category.OTHER, "general_agent")
    ]
)
def test_classify_routing(text, expected_category, expected_agent):
    input_text = f"TEST_{text}"  # <-- prefix testowy

    try:
        response = client.post("/classify", json={"text": input_text})
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == expected_category
        assert data["route"]["agent_name"] == expected_agent
        assert data["summary"] == input_text
    finally:
        delete_test_tickets()


@pytest.mark.parametrize(
    "text,expected_category,expected_agent",
    [
        ("Mam pilny problem z fakturą za ostatni miesiąc.", Category.FINANCE, "finance_invoice_agent"),
        ("Nie mogę zalogować się do VPN.", Category.IT_SUPPORT, "it_access_agent"),
        ("Chcę zgłosić urlop na przyszły tydzień.", Category.HR, "hr_leave_agent"),
        ("Pytanie ogólne do systemu.", Category.OTHER, "general_agent")
    ]
)
def test_process_routing_and_executed_action(text, expected_category, expected_agent):
    input_text = f"TEST_{text}"  # <-- prefix testowy

    try:
        response = client.post("/process", json={"text": input_text})
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == expected_category
        assert data["route"]["agent_name"] == expected_agent
        assert data["summary"] == input_text
        executed = data["executed_action"]
        assert executed["action_type"] == data["route"]["action_type"]
        assert executed["target_department"] == data["route"]["department"]
        assert executed["status"] == "SIMULATED"
    finally:
        delete_test_tickets()