def test_update_ticket_status(client):
    # Najpierw tworzymy zgłoszenie przez /process
    create_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "CHAT"
        },
    )

    assert create_response.status_code == 200

    # /process nie zwraca id, więc pobieramy zapisane zgłoszenia
    tickets_response = client.get("/tickets")

    assert tickets_response.status_code == 200

    tickets = tickets_response.json()

    assert len(tickets) > 0

    # Bierzemy najnowsze zgłoszenie.
    # Zakładamy, że /tickets zwraca listę od najnowszego albo że ostatni rekord ma największe id.
    latest_ticket = max(tickets, key=lambda ticket: ticket["id"])
    ticket_id = latest_ticket["id"]

    # Teraz zmieniamy status
    update_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "IN_PROGRESS"
        },
    )

    assert update_response.status_code == 200

    updated_ticket = update_response.json()

    assert updated_ticket["id"] == ticket_id
    assert updated_ticket["ticket_status"] == "IN_PROGRESS"


def test_update_ticket_status_ticket_not_found(client):
    response = client.patch(
        "/tickets/999999/status",
        json={
            "ticket_status": "IN_PROGRESS"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_update_ticket_status_invalid_status(client):
    response = client.patch(
        "/tickets/1/status",
        json={
            "ticket_status": "INVALID_STATUS"
        },
    )

    assert response.status_code == 422

def test_update_ticket_status_invalid_transition_from_new_to_closed(client):
    create_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "CHAT"
        },
    )

    assert create_response.status_code == 200

    tickets_response = client.get("/tickets")
    assert tickets_response.status_code == 200

    tickets = tickets_response.json()
    latest_ticket = max(tickets, key=lambda ticket: ticket["id"])
    ticket_id = latest_ticket["id"]

    response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "CLOSED"
        },
    )

    assert response.status_code == 400
    assert "Invalid ticket status transition" in response.json()["detail"]


def test_update_ticket_status_valid_full_flow(client):
    create_response = client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem.",
            "source_channel": "CHAT"
        },
    )

    assert create_response.status_code == 200

    tickets_response = client.get("/tickets")
    assert tickets_response.status_code == 200

    tickets = tickets_response.json()
    latest_ticket = max(tickets, key=lambda ticket: ticket["id"])
    ticket_id = latest_ticket["id"]

    response_1 = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "IN_PROGRESS"
        },
    )

    assert response_1.status_code == 200
    assert response_1.json()["ticket_status"] == "IN_PROGRESS"

    response_2 = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "WAITING_FOR_USER"
        },
    )

    assert response_2.status_code == 200
    assert response_2.json()["ticket_status"] == "WAITING_FOR_USER"

    response_3 = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "RESOLVED"
        },
    )

    assert response_3.status_code == 200
    assert response_3.json()["ticket_status"] == "RESOLVED"

    response_4 = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "CLOSED"
        },
    )

    assert response_4.status_code == 200
    assert response_4.json()["ticket_status"] == "CLOSED"

def test_update_ticket_status_same_status_is_allowed(client):
    create_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "CHAT"
        },
    )

    assert create_response.status_code == 200

    tickets_response = client.get("/tickets")
    assert tickets_response.status_code == 200

    tickets = tickets_response.json()
    latest_ticket = max(tickets, key=lambda ticket: ticket["id"])
    ticket_id = latest_ticket["id"]

    # NEW -> IN_PROGRESS
    first_update = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "IN_PROGRESS"
        },
    )

    assert first_update.status_code == 200
    assert first_update.json()["ticket_status"] == "IN_PROGRESS"

    # IN_PROGRESS -> IN_PROGRESS
    second_update = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "ticket_status": "IN_PROGRESS"
        },
    )

    assert second_update.status_code == 200
    assert second_update.json()["ticket_status"] == "IN_PROGRESS"