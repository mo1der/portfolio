from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.error_handlers import app_error_handler
from app.exceptions import AppError


def test_app_error_handler_returns_structured_json():
    test_app = FastAPI()
    test_app.add_exception_handler(AppError, app_error_handler)

    @test_app.get("/raise-app-error")
    def raise_app_error():
        raise AppError(
            message="Test application error",
            details={"field": "text"},
        )

    client = TestClient(test_app)

    response = client.get("/raise-app-error")

    assert response.status_code == 400
    assert response.json() == {
        "error": "AppError",
        "message": "Test application error",
        "details": {"field": "text"},
    }