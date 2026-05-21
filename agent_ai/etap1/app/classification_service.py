from app.schemas import ClassificationResponse, ProcessResponse, ExecutedAction
from app.agent_router import route_message

def build_process_response(category, priority, summary, suggested_action, source, text) -> ProcessResponse:
    route = route_message(category, text)

    # tworzymy symulowaną akcję dla RULE_BASED lub AI
    executed_action = ExecutedAction(
        action_type=f"CREATE_{category}_TICKET",
        status="SIMULATED",
        message=f"Utworzono symulowane zgłoszenie do działu {category}."
    )

    return ProcessResponse(
        category=category,
        priority=priority,
        summary=summary,
        suggested_action=suggested_action,
        source=source,
        route=route,
        executed_action=executed_action
    )