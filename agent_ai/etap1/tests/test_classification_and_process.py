import pytest

from app.schemas import Category


@pytest.mark.parametrize(
    "text,expected_category,expected_agent",
    [
        ("Mam pilny problem z fakturą za ostatni miesiąc.", Category.FINANCE, "finance_invoice_agent"),
        ("Nie mogę zalogować się do VPN.", Category.IT_SUPPORT, "it_access_agent"),
        ("Chcę zgłosić urlop na przyszły tydzień.", Category.HR, "hr_leave_agent"),
        ("Pytanie ogólne do systemu.", Category.OTHER, "general_agent"),
    ],
)
def test_classify_routing(client, text, expected_category, expected_agent):
    input_text = f"TEST_{text}"

    response = client.post("/classify", json={"text": input_text})

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == expected_category.value
    assert data["route"]["agent_name"] == expected_agent
    assert data["summary"] == input_text


@pytest.mark.parametrize(
    "text,expected_category,expected_agent",
    [
        ("Mam pilny problem z fakturą za ostatni miesiąc.", Category.FINANCE, "finance_invoice_agent"),
        ("Nie mogę zalogować się do VPN.", Category.IT_SUPPORT, "it_access_agent"),
        ("Chcę zgłosić urlop na przyszły tydzień.", Category.HR, "hr_leave_agent"),
        ("Pytanie ogólne do systemu.", Category.OTHER, "general_agent"),
    ],
)
def test_process_routing_and_executed_action(client, text, expected_category, expected_agent):
    input_text = f"TEST_{text}"

    response = client.post("/process", json={"text": input_text})

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == expected_category.value
    assert data["route"]["agent_name"] == expected_agent
    assert data["summary"] == input_text

    executed = data["executed_action"]

    assert executed["action_type"] == data["route"]["action_type"]
    assert executed["target_department"] == data["route"]["department"]
    assert executed["status"] == "SIMULATED"