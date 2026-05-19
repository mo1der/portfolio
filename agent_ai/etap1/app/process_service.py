from app.action_agent import choose_action
from app.action_executor import execute_action
from app.agent_router import route_message
from app.schemas import ClassificationRequest, ProcessResponse


def process_message(request: ClassificationRequest) -> ProcessResponse:
    classification = route_message(request.text)

    action_type = choose_action(classification)
    executed_action = execute_action(action_type)

    return ProcessResponse(
        category=classification.category,
        priority=classification.priority,
        summary=classification.summary,
        suggested_action=classification.suggested_action,
        source=classification.source,
        executed_action=executed_action,
    )