from app.schemas import ClassificationResponse, ProcessResponse, SourceChannel
from app.agent_router import route_message
from app.action_executor import execute_action
from app.intent_classifier import classify_intent
from app.action_router import route_action

def build_classification_response(
    category,
    priority,
    summary,
    suggested_action,
    source,
    text,
) -> ClassificationResponse:
    route = route_message(category, text)
    intent = classify_intent(text)
    action_type = route_action(category, intent)
    executed_action = execute_action(action_type)

    return ClassificationResponse(
        category=category,
        priority=priority,
        intent=intent,
        summary=summary,
        suggested_action=suggested_action,
        source=source,
        route=route,
        executed_action=executed_action,
    )


def build_process_response(
    category,
    priority,
    summary,
    suggested_action,
    source,
    text,
    source_channel=SourceChannel.API,
) -> ProcessResponse:
    route = route_message(category, text)
    intent = classify_intent(text)
    action_type = route_action(category, intent)
    executed_action = execute_action(action_type)

    return ProcessResponse(
        category=category,
        priority=priority,
        intent=intent,
        summary=summary,
        suggested_action=suggested_action,
        source=source,
        source_channel=source_channel,
        route=route,
        executed_action=executed_action,
    )