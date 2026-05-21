from app.schemas import ActionType, Category, ClassificationResponse, Priority


def choose_action(classification: ClassificationResponse) -> ActionType:
    if classification.priority == Priority.LOW:
        return ActionType.MARK_AS_LOW_PRIORITY

    if classification.category == Category.FINANCE:
        return ActionType.CREATE_FINANCE_TICKET

    if classification.category == Category.IT_SUPPORT:
        return ActionType.CREATE_IT_SUPPORT_TICKET

    if classification.category == Category.HR:
        return ActionType.CREATE_HR_TICKET

    if classification.priority == Priority.HIGH:
        return ActionType.ESCALATE_TO_MANAGER

    return ActionType.SEND_TO_GENERAL_QUEUE