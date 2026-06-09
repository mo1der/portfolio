def test_assign_ticket_to_team(client):
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

    assign_response = client.patch(
        f"/tickets/{ticket_id}/assign",
        json={
            "assigned_to": "finance_team",
        },
    )

    assert assign_response.status_code == 200

    ticket = assign_response.json()

    assert ticket["id"] == ticket_id
    assert ticket["assigned_to"] == "finance_team"


def test_assign_ticket_to_person(client):
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

    assign_response = client.patch(
        f"/tickets/{ticket_id}/assign",
        json={
            "assigned_to": "anna.kowalska",
        },
    )

    assert assign_response.status_code == 200

    ticket = assign_response.json()

    assert ticket["assigned_to"] == "anna.kowalska"


def test_assign_ticket_ticket_not_found(client):
    response = client.patch(
        "/tickets/999999/assign",
        json={
            "assigned_to": "finance_team",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


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
    tickets = tickets_response.json()
    latest_ticket = max(tickets, key=lambda ticket: ticket["id"])
    ticket_id = latest_ticket["id"]

    response = client.patch(
        f"/tickets/{ticket_id}/assign",
        json={
            "assigned_to": "   ",
        },
    )

    assert response.status_code == 422