def test_filter_tickets_by_category(client):
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "CHAT",
        },
    )

    client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem.",
            "source_channel": "CHAT",
        },
    )

    response = client.get("/tickets?category=FINANCE")

    assert response.status_code == 200

    tickets = response.json()

    assert len(tickets) >= 1
    assert all(ticket["category"] == "FINANCE" for ticket in tickets)


def test_filter_tickets_by_source_channel(client):
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "EMAIL",
        },
    )

    client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem.",
            "source_channel": "CHAT",
        },
    )

    response = client.get("/tickets?source_channel=EMAIL")

    assert response.status_code == 200

    tickets = response.json()

    assert len(tickets) >= 1
    assert all(ticket["source_channel"] == "EMAIL" for ticket in tickets)


def test_filter_tickets_by_status(client):
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "CHAT",
        },
    )

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

    response = client.get("/tickets?status=IN_PROGRESS")

    assert response.status_code == 200

    tickets = response.json()

    assert len(tickets) >= 1
    assert all(ticket["ticket_status"] == "IN_PROGRESS" for ticket in tickets)


def test_filter_tickets_by_combined_filters(client):
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "EMAIL",
        },
    )

    client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem.",
            "source_channel": "CHAT",
        },
    )

    response = client.get("/tickets?category=FINANCE&source_channel=EMAIL")

    assert response.status_code == 200

    tickets = response.json()

    assert len(tickets) >= 1
    assert all(
        ticket["category"] == "FINANCE" and ticket["source_channel"] == "EMAIL"
        for ticket in tickets
    )


def test_filter_tickets_invalid_category(client):
    response = client.get("/tickets?category=INVALID_CATEGORY")

    assert response.status_code == 422

def test_filter_tickets_by_assigned_to(client):
    create_response_1 = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "CHAT",
        },
    )

    assert create_response_1.status_code == 200

    create_response_2 = client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem.",
            "source_channel": "CHAT",
        },
    )

    assert create_response_2.status_code == 200

    tickets_response = client.get("/tickets")
    assert tickets_response.status_code == 200

    tickets = tickets_response.json()
    sorted_tickets = sorted(tickets, key=lambda ticket: ticket["id"], reverse=True)

    first_ticket_id = sorted_tickets[0]["id"]
    second_ticket_id = sorted_tickets[1]["id"]

    assign_response_1 = client.patch(
        f"/tickets/{first_ticket_id}/assign",
        json={
            "assigned_to": "finance_team",
        },
    )

    assert assign_response_1.status_code == 200

    assign_response_2 = client.patch(
        f"/tickets/{second_ticket_id}/assign",
        json={
            "assigned_to": "it_team",
        },
    )

    assert assign_response_2.status_code == 200

    response = client.get("/tickets?assigned_to=finance_team")

    assert response.status_code == 200

    filtered_tickets = response.json()

    assert len(filtered_tickets) >= 1
    assert all(ticket["assigned_to"] == "finance_team" for ticket in filtered_tickets)