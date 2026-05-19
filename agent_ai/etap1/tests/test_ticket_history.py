from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_classify_saves_ticket_history():
    response = client.post(
        "/classify",
        json={"text": "Mam pilny problem z fakturą za ostatni miesiąc."},
    )

    assert response.status_code == 200

    history_response = client.get("/tickets")

    assert history_response.status_code == 200

    tickets = history_response.json()

    assert len(tickets) >= 1

    latest_ticket = tickets[0]

    assert latest_ticket["input_text"] == "Mam pilny problem z fakturą za ostatni miesiąc."
    assert latest_ticket["category"] == "FINANCE"
    assert latest_ticket["priority"] == "HIGH"
    assert latest_ticket["summary"]
    assert latest_ticket["suggested_action"]
    assert latest_ticket["created_at"]