def test_search_tickets_by_input_text(client):
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą numer ABC123.",
            "source_channel": "CHAT",
        },
    )

    client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem do systemu.",
            "source_channel": "CHAT",
        },
    )

    response = client.get("/tickets?search=ABC123")

    assert response.status_code == 200

    data = response.json()
    tickets = data["items"]

    assert len(tickets) == 1
    assert tickets[0]["input_text"] == "Mam problem z fakturą numer ABC123."
    assert data["total"] == 1


def test_search_tickets_by_summary(client):
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "CHAT",
        },
    )

    response = client.get("/tickets?search=fakturą")

    assert response.status_code == 200

    data = response.json()
    tickets = data["items"]

    assert len(tickets) >= 1
    assert any("faktur" in ticket["summary"].lower() for ticket in tickets)


def test_search_tickets_no_results(client):
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "CHAT",
        },
    )

    response = client.get("/tickets?search=TEKST_KTOREGO_NIE_MA_999")

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
    assert data["has_next"] is False
    assert data["has_previous"] is False


def test_search_tickets_with_category_filter(client):
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą TEST_SEARCH_FINANCE.",
            "source_channel": "CHAT",
        },
    )

    client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem TEST_SEARCH_IT.",
            "source_channel": "CHAT",
        },
    )

    response = client.get("/tickets?search=TEST_SEARCH&category=FINANCE")

    assert response.status_code == 200

    data = response.json()
    tickets = data["items"]

    assert len(tickets) == 1
    assert tickets[0]["category"] == "FINANCE"
    assert "TEST_SEARCH_FINANCE" in tickets[0]["input_text"]


def test_search_tickets_with_pagination(client):
    for i in range(3):
        client.post(
            "/process",
            json={
                "text": f"Mam problem SEARCH_PAGE_{i}.",
                "source_channel": "CHAT",
            },
        )

    response = client.get("/tickets?search=SEARCH_PAGE&limit=2&offset=0&sort_by=id&sort_order=asc")

    assert response.status_code == 200

    data = response.json()
    tickets = data["items"]

    assert len(tickets) == 2
    assert data["total"] == 3
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert data["has_next"] is True
    assert data["has_previous"] is False
