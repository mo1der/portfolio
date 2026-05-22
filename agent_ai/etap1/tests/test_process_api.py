from app.schemas import Category, Priority


def test_process_endpoint_for_finance_high_priority(client):
    input_text = "TEST_Mam pilny problem z fakturą."

    response = client.post("/process", json={"text": input_text})

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == Category.FINANCE.value
    assert data["priority"] == Priority.HIGH.value
    assert data["summary"] == input_text

    assert "route" in data
    assert data["route"]["agent_name"] == "finance_invoice_agent"

    assert "executed_action" in data
    assert data["executed_action"]["status"] == "SIMULATED"