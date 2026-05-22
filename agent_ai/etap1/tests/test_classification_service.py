import pytest


@pytest.mark.parametrize(
    "text,expected_agent",
    [
        ("Mam problem z fakturą", "finance_invoice_agent"),
        ("Nie mogę zalogować się do VPN", "it_access_agent"),
        ("Chcę złożyć wniosek urlopowy", "hr_leave_agent"),
        ("Pytanie ogólne do systemu", "general_agent"),
    ],
)
def test_classify_routing(client, text, expected_agent):
    input_text = f"TEST_{text}"

    response = client.post("/classify", json={"text": input_text})

    assert response.status_code == 200

    data = response.json()

    assert "route" in data
    assert data["route"]["agent_name"] == expected_agent
    assert data["summary"] == input_text