from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.agent_router import route_message
from app.process_service import process_message
from app.schemas import ClassificationRequest, ClassificationResponse, ProcessResponse

from app.core.settings import settings

from app.error_handlers import (
    app_error_handler,
    generic_error_handler,
    validation_error_handler,
)

from app.exceptions import AppError
from app.middleware import RequestLoggingMiddleware

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_exception_handler(RequestValidationError, validation_error_handler)

app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

@app.get("/")
def root():
    return {
        "message": "AI Classifier Backend działa"
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "ai_enabled": settings.ai_enabled,
    }

@app.post("/classify", response_model=ClassificationResponse)
def classify(request: ClassificationRequest):
    return route_message(request.text)


@app.post("/process", response_model=ProcessResponse)
def process(request: ClassificationRequest):
    return process_message(request)