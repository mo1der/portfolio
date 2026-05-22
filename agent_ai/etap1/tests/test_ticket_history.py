from uuid import uuid4


def test_classify_saves_ticket_history(client):
    unique_id = uuid4()
    input_text = f"TEST_HISTORY_{unique_id} Mam pilny problem z fakturą za ostatni miesiąc."

    response = client.post(
        "/classify",
        json={"text": input_text},
    )

    assert response.status_code == 200

    history_response = client.get("/tickets")

    assert history_response.status_code == 200

    tickets = history_response.json()

    matching_tickets = [
        ticket for ticket in tickets
        if ticket["input_text"] == input_text
    ]

    assert len(matching_tickets) == 1

    saved_ticket = matching_tickets[0]

    assert saved_ticket["input_text"] == input_text
    assert saved_ticket["category"] == response.json()["category"]
    assert saved_ticket["priority"] == response.json()["priority"]