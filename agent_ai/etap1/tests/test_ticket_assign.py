def test_assign_ticket_blank_assigned_to(client):
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

    tickets = tickets_response.json()["items"]
    latest_ticket = max(tickets, key=lambda ticket: ticket["id"])
    ticket_id = latest_ticket["id"]

    response = client.patch(
        f"/tickets/{ticket_id}/assign",
        json={
            "assigned_to": "   ",
        },
    )

    assert response.status_code == 422