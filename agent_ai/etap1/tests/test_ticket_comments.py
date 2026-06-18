def test_add_ticket_comment(client):
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

    comment_response = client.post(
        f"/tickets/{ticket_id}/comments",
        json={
            "comment_text": "Poproszono użytkownika o numer faktury.",
            "author": "SYSTEM",
        },
    )

    assert comment_response.status_code == 200

    comment = comment_response.json()

    assert comment["ticket_id"] == ticket_id
    assert comment["comment_text"] == "Poproszono użytkownika o numer faktury."
    assert comment["author"] == "SYSTEM"
    assert "created_at" in comment


def test_get_ticket_comments(client):
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

    tickets = tickets_response.json()["items"]
    latest_ticket = max(tickets, key=lambda ticket: ticket["id"])
    ticket_id = latest_ticket["id"]

    client.post(
        f"/tickets/{ticket_id}/comments",
        json={
            "comment_text": "Pierwszy komentarz.",
            "author": "SYSTEM",
        },
    )

    client.post(
        f"/tickets/{ticket_id}/comments",
        json={
            "comment_text": "Drugi komentarz.",
            "author": "SYSTEM",
        },
    )

    comments_response = client.get(f"/tickets/{ticket_id}/comments")

    assert comments_response.status_code == 200

    comments = comments_response.json()

    assert len(comments) == 2
    assert comments[0]["comment_text"] == "Pierwszy komentarz."
    assert comments[1]["comment_text"] == "Drugi komentarz."


def test_add_ticket_comment_ticket_not_found(client):
    response = client.post(
        "/tickets/999999/comments",
        json={
            "comment_text": "Komentarz do nieistniejącego zgłoszenia.",
            "author": "SYSTEM",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_get_ticket_comments_ticket_not_found(client):
    response = client.get("/tickets/999999/comments")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_add_ticket_comment_blank_text(client):
    create_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "CHAT",
        },
    )

    assert create_response.status_code == 200

    tickets_response = client.get("/tickets")
    tickets = tickets_response.json()["items"]
    latest_ticket = max(tickets, key=lambda ticket: ticket["id"])
    ticket_id = latest_ticket["id"]

    response = client.post(
        f"/tickets/{ticket_id}/comments",
        json={
            "comment_text": "   ",
            "author": "SYSTEM",
        },
    )

    assert response.status_code == 422