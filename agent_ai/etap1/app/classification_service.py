from app.ai_classifier import classify_text_with_ai
from app.classifier import classify_text
from app.schemas import ClassificationResponse


def classify_message(text: str) -> ClassificationResponse:
    try:
        return classify_text_with_ai(text)
    except Exception as e:
        print(f"AI classifier failed, using fallback. Error: {repr(e)}")
        return classify_text(text)