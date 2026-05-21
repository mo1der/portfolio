from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.database import engine

client = TestClient(app)


def delete_test_ticket(input_text: str):
    """
    Usuwa tylko rekord testowy utworzony przez ten konkretny test.
    Nie czyści całej tabeli ticket_history.
    """
    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM ticket_history WHERE input_text = :input_text"),
            {"input_text": input_text},
        )


def test_classify_saves_ticket_history():
    unique_id = uuid4()
    input_text = f"TEST_HISTORY_{unique_id} Mam pilny problem z fakturą za ostatni miesiąc."

    try:
        response = client.post(
            "/classify",
            json={"text": input_text},
        )

        assert response.status_code == 200

        history_response = client.get("/tickets")

        assert history_response.status_code == 200

        tickets = history_response.json()

        matching_tickets = [
            ticket for ticket in tickets
            if ticket["input_text"] == input_text
        ]

        assert len(matching_tickets) == 1

        saved_ticket = matching_tickets[0]

        assert saved_ticket["input_text"] == input_text
        assert saved_ticket["category"] == response.json()["category"]
        assert saved_ticket["priority"] == response.json()["priority"]

    finally:
        delete_test_ticket(input_text)