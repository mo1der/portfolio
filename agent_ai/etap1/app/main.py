from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import pandas as pd

from app.database import Base, engine, get_db
import app.models
from app.repositories import get_ticket_history, save_ticket_history, update_ticket_status, get_ticket_by_id
from app.ticket_status_rules import is_status_transition_allowed
from app.agent_router import route_message
from app.response_builders import build_process_response
from app.schemas import ClassificationRequest, ProcessResponse, TicketHistoryResponse, TicketStatusUpdateRequest, SourceChannel, EmailAnalyzeRequest
from app.classifier import classify_text_rule_based
from app.ai_classifier import classify_text_with_ai
from app.core.settings import settings
from app.error_handlers import app_error_handler, generic_error_handler, validation_error_handler
from app.exceptions import AppError
from app.middleware import RequestLoggingMiddleware
from app.ai_usage_limiter import ai_usage_limiter

from scripts.sync_sqlite_to_mysql import sync

from app.intent_classifier import classify_intent
from app.action_router import route_action
from app.action_executor import execute_action

# FastAPI app
app = FastAPI(title=settings.app_name, version=settings.app_version)

# Tworzymy wszystkie tabele w bazie (jeśli nie istnieją)
Base.metadata.create_all(bind=engine)

# Middleware
app.add_middleware(RequestLoggingMiddleware)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# -----------------------------
# AI flag (w testach można patchować classify_text_with_ai)
USE_AI = settings.ai_enabled
# -----------------------------

def classify_text(text: str) -> dict:
    """
    Hybrydowa klasyfikacja:
    1. Najpierw klasyfikator regułowy.
    2. Jeśli reguły rozpoznają kategorię inną niż OTHER, nie używamy AI.
    3. Jeśli reguły zwrócą OTHER, próbujemy AI.
    4. Jeśli AI jest wyłączone, limit przekroczony, tekst za długi albo AI ma błąd,
       zostaje wynik RULE_BASED.
    """
    rule_based_result = classify_text_rule_based(text)

    rule_based_category = rule_based_result["category"]
    rule_based_category_value = (
        rule_based_category.value
        if hasattr(rule_based_category, "value")
        else rule_based_category
    )

    if rule_based_category_value != "OTHER":
        return rule_based_result

    if not USE_AI:
        return rule_based_result

    if len(text) > settings.ai_max_input_chars:
        print(
            f"Input too long for AI ({len(text)} chars), "
            f"limit is {settings.ai_max_input_chars}. Using rule-based fallback."
        )
        return rule_based_result

    if not ai_usage_limiter.can_use_ai(settings.ai_daily_request_limit):
        print(
            f"AI daily request limit reached "
            f"({settings.ai_daily_request_limit}). Using rule-based fallback."
        )
        return rule_based_result

    try:
        ai_usage_limiter.register_ai_request()
        return classify_text_with_ai(text)
    except Exception as error:
        print(f"AI classifier failed, using rule-based fallback. Error: {error}")
        return rule_based_result

# -----------------------------
# Root endpoint
@app.get("/")
def root():
    return {"message": "AI Classifier Backend działa"}

# -----------------------------
# Health check
@app.get("/health")
def health_check():
    database_dialect = engine.dialect.name
    database_name = None
    try:
        with engine.connect() as connection:
            if database_dialect == "mysql":
                result = connection.execute(text("SELECT DATABASE();"))
                database_name = result.scalar()
            elif database_dialect == "sqlite":
                database_name = settings.database_url.split("/")[-1]  # np. ai_classifier_test.db
            else:
                database_name = "unknown"
    except Exception as error:
        database_name = f"database check error: {error}"

    return {
        "status": "ok",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "ai_enabled": settings.ai_enabled,
        "database": database_name,
        "dialect": database_dialect,
    }

@app.get("/ai/status")
def ai_status():
    usage = ai_usage_limiter.get_usage()

    return {
        "ai_enabled": settings.ai_enabled,
        "model": settings.openai_model,
        "daily_request_limit": settings.ai_daily_request_limit,
        "request_count_today": usage["request_count"],
        "remaining_requests_today": max(
            settings.ai_daily_request_limit - usage["request_count"],
            0,
        ),
        "max_input_chars": settings.ai_max_input_chars,
        "max_output_tokens": settings.ai_max_output_tokens,
    }

# -----------------------------
# Endpoint /classify

@app.post("/classify", response_model=ProcessResponse)
def classify_message(
    request: ClassificationRequest,
    db: Session = Depends(get_db),
):
    text = request.text
    source_channel = request.source_channel

    # Klasyfikacja
    classification = classify_text(text)

    # Odpowiedź
    response = build_process_response(
        category=classification["category"].value if hasattr(classification["category"], "value") else classification["category"],
        priority=classification["priority"].value if hasattr(classification["priority"], "value") else classification["priority"],
        summary=classification["summary"],
        suggested_action=classification["suggested_action"],
        source=classification["source"],
        text=text,
        source_channel=source_channel,
    )

    # Zapis do bazy
    save_ticket_history(db=db, input_text=text, classification=response)
    return response

# -----------------------------
# Endpoint /process

@app.post("/emails/analyze", response_model=ProcessResponse)
def analyze_email(
    request: EmailAnalyzeRequest,
    db: Session = Depends(get_db),
):
    email_text = (
        f"Nadawca: {request.from_email}\n"
        f"Temat: {request.subject}\n"
        f"Treść: {request.body}"
    )

    classification = classify_text(email_text)

    response = build_process_response(
        category=classification["category"].value if hasattr(classification["category"], "value") else classification["category"],
        priority=classification["priority"].value if hasattr(classification["priority"], "value") else classification["priority"],
        summary=classification["summary"],
        suggested_action=classification["suggested_action"],
        source=classification["source"],
        text=email_text,
        source_channel=SourceChannel.EMAIL,
    )

    save_ticket_history(db=db, input_text=email_text, classification=response)
    return response

@app.post("/process", response_model=ProcessResponse)
def process(request: ClassificationRequest, db: Session = Depends(get_db)):
    text = request.text
    source_channel = request.source_channel

    classification = classify_text(text)

    category = (
        classification["category"].value
        if hasattr(classification["category"], "value")
        else classification["category"]
    )

    priority = (
        classification["priority"].value
        if hasattr(classification["priority"], "value")
        else classification["priority"]
    )

    intent = classify_intent(text)

    route = route_message(category, text)

    action_type = route_action(category, intent)
    executed_action = execute_action(action_type)

    response = ProcessResponse(
        category=category,
        priority=priority,
        intent=intent,
        summary=classification["summary"],
        suggested_action=classification["suggested_action"],
        source=classification["source"],
        source_channel=source_channel,
        route=route,
        executed_action=executed_action,
    )

    save_ticket_history(db=db, input_text=text, classification=response)
    return response

# -----------------------------

def ticket_to_response(ticket):
    return {
        "id": ticket.id,
        "input_text": ticket.input_text,
        "source_channel": ticket.source_channel,

        "category": ticket.category,
        "priority": ticket.priority,
        "intent": ticket.intent,
        "ticket_status": ticket.ticket_status,

        "summary": ticket.summary,
        "suggested_action": ticket.suggested_action,
        "source": ticket.source,

        "executed_action_type": ticket.executed_action_type,
        "executed_action_status": ticket.executed_action_status,
        "executed_action_message": ticket.executed_action_message,

        "route_agent_name": ticket.route_agent_name,
        "route_department": ticket.route_department,
        "route_reason": ticket.route_reason,

        # baza ma starą nazwę, API pokazuje nową nazwę
        "route_default_action_type": ticket.route_action_type,

        "created_at": ticket.created_at,
    }


# -----------------------------

@app.patch(
    "/tickets/{ticket_id}/status",
    response_model=TicketHistoryResponse,
    responses={
        400: {
            "description": "Invalid ticket status transition",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid ticket status transition: CLOSED -> NEW"
                    }
                }
            },
        },
        404: {
            "description": "Ticket not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Ticket not found"
                    }
                }
            },
        },
        422: {
            "description": "Validation error - invalid ticket_status value",
        },
    },
)
def patch_ticket_status(
    ticket_id: int,
    request: TicketStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    ticket = get_ticket_by_id(db=db, ticket_id=ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    if not is_status_transition_allowed(
        current_status=ticket.ticket_status,
        new_status=request.ticket_status,
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid ticket status transition: "
                f"{ticket.ticket_status} -> {request.ticket_status.value}"
            ),
        )

    updated_ticket = update_ticket_status(
        db=db,
        ticket_id=ticket_id,
        ticket_status=request.ticket_status,
    )

    return ticket_to_response(updated_ticket)


# -----------------------------
# Endpoint /tickets
@app.get("/tickets", response_model=list[TicketHistoryResponse])
def get_tickets(db: Session = Depends(get_db)):
    tickets = get_ticket_history(db)
    return [ticket_to_response(ticket) for ticket in tickets]

# -----------------------------
# Endpoint /stats
@app.get("/stats")
def ticket_stats(days: int = Query(30, description="Ilość dni do wstecznej analizy"), db: Session = Depends(get_db)):
    query = "SELECT * FROM ticket_history"
    df = pd.read_sql(query, db.bind)
    df['created_at'] = pd.to_datetime(df['created_at'])

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    df_filtered = df[(df['created_at'] >= start_date) & (df['created_at'] <= end_date)]

    if df_filtered.empty:
        return {"message": f"Brak zgłoszeń w ostatnich {days} dniach."}

    stats = {
        "count_by_category": df_filtered['category'].value_counts().to_dict(),
        "count_by_priority": df_filtered['priority'].value_counts().to_dict(),
        "count_by_status": df_filtered['executed_action_status'].value_counts().to_dict(),
        "top_agents": df_filtered['route_agent_name'].value_counts().head(10).to_dict(),
        "total_tickets": len(df_filtered)
    }
    return stats

# -----------------------------
# Endpoint /sync/sqlite-to-mysql
# -----------------------------
@app.post("/sync/sqlite-to-mysql")
def sync_sqlite_to_mysql():
    """
    Ręczna synchronizacja danych z awaryjnej SQLite ai_classifier.db do MySQL.

    Używane po sytuacji awaryjnej:
    - MySQL nie działał,
    - aplikacja zapisała zgłoszenia do ai_classifier.db,
    - MySQL wrócił,
    - uruchamiamy synchronizację.
    """
    try:
        result = sync()

        if result is None:
            return {
                "status": "completed",
                "message": "Synchronizacja została uruchomiona. Szczegóły sprawdź w logach serwera.",
            }

        return {
            "status": "completed",
            "result": result,
        }

    except Exception as error:
        return {
            "status": "failed",
            "message": str(error),
        }