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