def test_ticket_status_history_is_created_after_status_change(client):
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

    update_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "IN_PROGRESS",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["ticket_status"] == "IN_PROGRESS"

    history_response = client.get(f"/tickets/{ticket_id}/status-history")

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert history[0]["ticket_id"] == ticket_id
    assert history[0]["old_status"] == "NEW"
    assert history[0]["new_status"] == "IN_PROGRESS"
    assert history[0]["changed_by"] == "SYSTEM"
    assert "changed_at" in history[0]


def test_ticket_status_history_not_created_for_same_status(client):
    create_response = client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem.",
            "source_channel": "CHAT",
        },
    )

    assert create_response.status_code == 200

    tickets_response = client.get("/tickets")
    assert tickets_response.status_code == 200

    tickets = tickets_response.json()
    latest_ticket = max(tickets, key=lambda ticket: ticket["id"])
    ticket_id = latest_ticket["id"]

    first_update = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "IN_PROGRESS",
        },
    )

    assert first_update.status_code == 200

    second_update = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "IN_PROGRESS",
        },
    )

    assert second_update.status_code == 200

    history_response = client.get(f"/tickets/{ticket_id}/status-history")

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert history[0]["old_status"] == "NEW"
    assert history[0]["new_status"] == "IN_PROGRESS"


def test_ticket_status_history_ticket_not_found(client):
    response = client.get("/tickets/999999/status-history")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"