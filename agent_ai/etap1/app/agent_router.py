from app.classification_service import classify_message
from app.schemas import ClassificationResponse


def route_message(text: str) -> ClassificationResponse:
    return classify_message(text)