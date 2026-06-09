def test_get_ticket_by_id(client):
    create_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "CHAT",
        },
    )

    assert create_response.status_code == 200

    tickets_response = client.get("/tickets")
    assert tickets_response.status_code == 200

    tickets = tickets_response.json()
    latest_ticket = max(tickets, key=lambda ticket: ticket["id"])
    ticket_id = latest_ticket["id"]

    response = client.get(f"/tickets/{ticket_id}")

    assert response.status_code == 200

    ticket = response.json()

    assert ticket["id"] == ticket_id
    assert ticket["input_text"] == "Mam problem z fakturą."
    assert ticket["category"] == "FINANCE"
    assert ticket["priority"] == "HIGH"
    assert ticket["ticket_status"] == "NEW"
    assert ticket["route_default_action_type"] == "CREATE_FINANCE_TICKET"


def test_get_ticket_by_id_not_found(client):
    response = client.get("/tickets/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"