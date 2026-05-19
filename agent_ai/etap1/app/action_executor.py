from app.schemas import ActionResult, ActionStatus, ActionType, Category


def execute_action(action_type: ActionType) -> ActionResult:
    if action_type == ActionType.CREATE_FINANCE_TICKET:
        return ActionResult(
            action_type=action_type,
            target_department=Category.FINANCE,
            status=ActionStatus.SIMULATED,
            message="Utworzono symulowane zgłoszenie do działu finansów.",
        )

    if action_type == ActionType.CREATE_IT_TICKET:
        return ActionResult(
            action_type=action_type,
            target_department=Category.IT_SUPPORT,
            status=ActionStatus.SIMULATED,
            message="Utworzono symulowane zgłoszenie do działu IT.",
        )

    if action_type == ActionType.CREATE_HR_CASE:
        return ActionResult(
            action_type=action_type,
            target_department=Category.HR,
            status=ActionStatus.SIMULATED,
            message="Utworzono symulowaną sprawę do działu HR.",
        )

    if action_type == ActionType.MARK_AS_LOW_PRIORITY:
        return ActionResult(
            action_type=action_type,
            target_department=Category.OTHER,
            status=ActionStatus.SIMULATED,
            message="Oznaczono sprawę jako niskiego priorytetu.",
        )

    if action_type == ActionType.ESCALATE_TO_MANAGER:
        return ActionResult(
            action_type=action_type,
            target_department=Category.OTHER,
            status=ActionStatus.SIMULATED,
            message="Sprawa została symulacyjnie eskalowana do managera.",
        )

    return ActionResult(
        action_type=ActionType.SEND_TO_GENERAL_QUEUE,
        target_department=Category.OTHER,
        status=ActionStatus.SIMULATED,
        message="Sprawa została przekazana do kolejki ogólnej.",
    )