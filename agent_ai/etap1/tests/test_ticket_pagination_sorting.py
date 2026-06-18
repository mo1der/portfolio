def test_tickets_limit(client):
    for i in range(3):
        response = client.post(
            "/process",
            json={
                "text": f"Mam problem z fakturą numer {i}.",
                "source_channel": "CHAT",
            },
        )
        assert response.status_code == 200

    response = client.get("/tickets?limit=2")

    assert response.status_code == 200

    data = response.json()
    tickets = data["items"]

    assert len(tickets) == 2
    assert data["limit"] == 2


def test_tickets_offset(client):
    for i in range(3):
        response = client.post(
            "/process",
            json={
                "text": f"Mam problem z logowaniem numer {i}.",
                "source_channel": "CHAT",
            },
        )
        assert response.status_code == 200

    first_page_response = client.get("/tickets?limit=1&offset=0&sort_by=id&sort_order=asc")
    second_page_response = client.get("/tickets?limit=1&offset=1&sort_by=id&sort_order=asc")

    assert first_page_response.status_code == 200
    assert second_page_response.status_code == 200

    first_page = first_page_response.json()["items"]
    second_page = second_page_response.json()["items"]

    assert len(first_page) == 1
    assert len(second_page) == 1
    assert first_page[0]["id"] != second_page[0]["id"]


def test_tickets_sort_by_id_asc(client):
    for i in range(3):
        response = client.post(
            "/process",
            json={
                "text": f"Mam problem z fakturą numer {i}.",
                "source_channel": "CHAT",
            },
        )
        assert response.status_code == 200

    response = client.get("/tickets?sort_by=id&sort_order=asc")

    assert response.status_code == 200

    tickets = response.json()["items"]
    ids = [ticket["id"] for ticket in tickets]

    assert ids == sorted(ids)


def test_tickets_sort_by_id_desc(client):
    for i in range(3):
        response = client.post(
            "/process",
            json={
                "text": f"Mam problem z fakturą numer {i}.",
                "source_channel": "CHAT",
            },
        )
        assert response.status_code == 200

    response = client.get("/tickets?sort_by=id&sort_order=desc")

    assert response.status_code == 200

    tickets = response.json()["items"]
    ids = [ticket["id"] for ticket in tickets]

    assert ids == sorted(ids, reverse=True)


def test_tickets_invalid_limit(client):
    response = client.get("/tickets?limit=0")

    assert response.status_code == 422


def test_tickets_invalid_offset(client):
    response = client.get("/tickets?offset=-1")

    assert response.status_code == 422


def test_tickets_invalid_sort_order(client):
    response = client.get("/tickets?sort_order=wrong")

    assert response.status_code == 422


def test_tickets_filters_with_pagination(client):
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

    response = client.get(
        "/tickets?category=FINANCE&source_channel=EMAIL&limit=1&offset=0"
    )

    assert response.status_code == 200

    data = response.json()
    tickets = data["items"]

    assert len(tickets) == 1
    assert data["limit"] == 1
    assert tickets[0]["category"] == "FINANCE"
    assert tickets[0]["source_channel"] == "EMAIL"