from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_export_tickets_csv_empty_database():
    response = client.get("/tickets/export/csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=tickets_export.csv" in response.headers["content-disposition"]

    content = decode_csv_response(response)

    assert "id\tcreated_at\tsource_channel\tcategory\tpriority\tintent\tticket_status" in content


def test_export_tickets_csv_after_process():
    process_response = client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "API",
        },
    )

    assert process_response.status_code == 200

    response = client.get("/tickets/export/csv")

    assert response.status_code == 200

    content = decode_csv_response(response)

    assert "Mam problem z fakturą." in content
    assert "FINANCE" in content
    assert "HIGH" in content


def test_export_tickets_csv_with_category_filter():
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą.",
            "source_channel": "API",
        },
    )

    client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem.",
            "source_channel": "API",
        },
    )

    response = client.get("/tickets/export/csv?category=FINANCE")

    assert response.status_code == 200

    content = decode_csv_response(response)

    assert "Mam problem z fakturą." in content
    assert "Mam problem z logowaniem." not in content


def test_export_tickets_csv_with_search_filter():
    client.post(
        "/process",
        json={
            "text": "Mam problem z fakturą ABC999.",
            "source_channel": "API",
        },
    )

    client.post(
        "/process",
        json={
            "text": "Mam problem z logowaniem.",
            "source_channel": "API",
        },
    )

    response = client.get("/tickets/export/csv?search=ABC999")

    assert response.status_code == 200

    content = decode_csv_response(response)

    assert "ABC999" in content
    assert "Mam problem z logowaniem." not in content


def test_export_tickets_csv_invalid_category():
    response = client.get("/tickets/export/csv?category=INVALID_CATEGORY")

    assert response.status_code == 422

def decode_csv_response(response):
    return response.content.decode("utf-16")