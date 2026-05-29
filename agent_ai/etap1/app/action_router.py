from app.schemas import Category, Intent, ActionType


def route_action(category: Category, intent: Intent) -> ActionType:
    if intent == Intent.CONTACT_HUMAN:
        return ActionType.ROUTE_TO_HUMAN

    if intent == Intent.THANKS:
        return ActionType.NO_ACTION

    if intent == Intent.CHECK_STATUS:
        if category == Category.FINANCE:
            return ActionType.CHECK_FINANCE_STATUS
        if category == Category.IT_SUPPORT:
            return ActionType.CHECK_IT_SUPPORT_STATUS
        if category == Category.HR:
            return ActionType.CHECK_HR_STATUS
        return ActionType.CHECK_OTHER_STATUS

    if intent == Intent.UPDATE_DATA:
        if category == Category.FINANCE:
            return ActionType.UPDATE_FINANCE_DATA
        if category == Category.IT_SUPPORT:
            return ActionType.UPDATE_IT_SUPPORT_DATA
        if category == Category.HR:
            return ActionType.UPDATE_HR_DATA
        return ActionType.UPDATE_OTHER_DATA

    if intent == Intent.COMPLAINT:
        if category == Category.FINANCE:
            return ActionType.ESCALATE_FINANCE_COMPLAINT
        if category == Category.IT_SUPPORT:
            return ActionType.ESCALATE_IT_SUPPORT_COMPLAINT
        if category == Category.HR:
            return ActionType.ESCALATE_HR_COMPLAINT
        return ActionType.ESCALATE_OTHER_COMPLAINT

    if intent == Intent.CREATE_TICKET:
        if category == Category.FINANCE:
            return ActionType.CREATE_FINANCE_TICKET
        if category == Category.IT_SUPPORT:
            return ActionType.CREATE_IT_SUPPORT_TICKET
        if category == Category.HR:
            return ActionType.CREATE_HR_TICKET
        return ActionType.CREATE_OTHER_TICKET

    if category == Category.OTHER:
        return ActionType.SEND_TO_GENERAL_QUEUE

    return ActionType.CREATE_OTHER_TICKET