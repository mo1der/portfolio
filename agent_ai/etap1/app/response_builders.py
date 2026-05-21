from app.schemas import ClassificationResponse, ProcessResponse, ActionResult, ActionType, ActionStatus, Category
from app.agent_router import route_message

def build_classification_response(category, priority, summary, suggested_action, source, text) -> ClassificationResponse:
    route = route_message(category, text)

    # Poprawne tworzenie ActionType z użyciem wartości Enum
    cat_name = category.value if hasattr(category, "value") else str(category)

    executed_action = ActionResult(
        action_type=ActionType[f"CREATE_{cat_name}_TICKET"],
        target_department=Category(category),
        status=ActionStatus.SIMULATED,
        message=f"Utworzono symulowane zgłoszenie do działu {cat_name}."
    )

    return ClassificationResponse(
        category=Category(category),
        priority=priority,
        summary=summary,
        suggested_action=suggested_action,
        source=source,
        route=route,
        executed_action=executed_action
    )

def build_process_response(category, priority, summary, suggested_action, source, text) -> ProcessResponse:
    route = route_message(category, text)

    cat_name = category.value if hasattr(category, "value") else str(category)

    executed_action = ActionResult(
        action_type=ActionType[f"CREATE_{cat_name}_TICKET"],
        target_department=Category(category),
        status=ActionStatus.SIMULATED,
        message=f"Utworzono symulowane zgłoszenie do działu {cat_name}."
    )

    return ProcessResponse(
        category=Category(category),
        priority=priority,
        summary=summary,
        suggested_action=suggested_action,
        source=source,
        route=route,
        executed_action=executed_action
    )