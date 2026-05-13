from app.ai_classifier import classify_text_with_ai
from app.classifier import classify_text
from app.logger import logger
from app.schemas import ClassificationResponse
from app.core.settings import settings



def classify_message(text: str) -> ClassificationResponse:
    if not settings.ai_enabled:
        logger.info("AI classifier disabled, using fallback")
        return classify_text(text)

    try:
        logger.info("Trying AI classifier")
        result = classify_text_with_ai(text)
        logger.info("AI classifier succeeded")
        return result
    except Exception as e:
        logger.warning(f"AI classifier failed, using fallback. Error: {repr(e)}")
        return classify_text(text)