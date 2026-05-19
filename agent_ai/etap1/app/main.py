from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.repositories import get_ticket_history, save_ticket_history


from fastapi.exceptions import RequestValidationError

from app.agent_router import route_message
from app.process_service import process_message

from app.schemas import ClassificationRequest, ClassificationResponse, ProcessResponse, TicketHistoryResponse


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

Base.metadata.create_all(bind=engine)

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
def classify_message(
    request: ClassificationRequest,
    db: Session = Depends(get_db),
):
    classification = route_message(request.text)

    save_ticket_history(
        db=db,
        input_text=request.text,
        classification=classification,
    )

    return classification

@app.post("/process", response_model=ProcessResponse)
def process(
    request: ClassificationRequest,
    db: Session = Depends(get_db),
):
    result = process_message(request)

    save_ticket_history(
        db=db,
        input_text=request.text,
        classification=result,
    )

    return result

@app.get("/tickets", response_model=list[TicketHistoryResponse])
def read_ticket_history(db: Session = Depends(get_db)):
    return get_ticket_history(db)
