from app.schemas import ActionResult, ActionStatus, ActionType, Category


def _get_target_department(action_type: ActionType) -> Category:
    if "FINANCE" in action_type.value:
        return Category.FINANCE

    if "IT_SUPPORT" in action_type.value:
        return Category.IT_SUPPORT

    if "HR" in action_type.value:
        return Category.HR

    return Category.OTHER


def execute_action(action_type: ActionType) -> ActionResult:
    if action_type == ActionType.CREATE_FINANCE_TICKET:
        return ActionResult(
            action_type=action_type,
            target_department=Category.FINANCE,
            status=ActionStatus.SIMULATED,
            message="Utworzono symulowane zgłoszenie do działu finansów.",
        )

    if action_type == ActionType.CREATE_IT_SUPPORT_TICKET:
        return ActionResult(
            action_type=action_type,
            target_department=Category.IT_SUPPORT,
            status=ActionStatus.SIMULATED,
            message="Utworzono symulowane zgłoszenie do działu IT.",
        )

    if action_type == ActionType.CREATE_HR_TICKET:
        return ActionResult(
            action_type=action_type,
            target_department=Category.HR,
            status=ActionStatus.SIMULATED,
            message="Utworzono symulowaną sprawę do działu HR.",
        )

    if action_type == ActionType.CREATE_OTHER_TICKET:
        return ActionResult(
            action_type=action_type,
            target_department=Category.OTHER,
            status=ActionStatus.SIMULATED,
            message="Utworzono symulowane zgłoszenie ogólne.",
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

    if action_type == ActionType.ROUTE_TO_HUMAN:
        return ActionResult(
            action_type=action_type,
            target_department=Category.OTHER,
            status=ActionStatus.SIMULATED,
            message="Sprawa została przekazana do obsługi przez człowieka.",
        )

    if action_type == ActionType.NO_ACTION:
        return ActionResult(
            action_type=action_type,
            target_department=Category.OTHER,
            status=ActionStatus.SIMULATED,
            message="Nie wykonano akcji, ponieważ wiadomość nie wymaga dalszej obsługi.",
        )

    if "CHECK" in action_type.value:
        return ActionResult(
            action_type=action_type,
            target_department=_get_target_department(action_type),
            status=ActionStatus.SIMULATED,
            message=f"Symulacja sprawdzenia statusu: {action_type.value}.",
        )

    if "UPDATE" in action_type.value:
        return ActionResult(
            action_type=action_type,
            target_department=_get_target_department(action_type),
            status=ActionStatus.SIMULATED,
            message=f"Symulacja aktualizacji danych: {action_type.value}.",
        )

    if "COMPLAINT" in action_type.value or "ESCALATE" in action_type.value:
        return ActionResult(
            action_type=action_type,
            target_department=_get_target_department(action_type),
            status=ActionStatus.SIMULATED,
            message=f"Symulacja eskalacji sprawy: {action_type.value}.",
        )

    return ActionResult(
        action_type=ActionType.SEND_TO_GENERAL_QUEUE,
        target_department=Category.OTHER,
        status=ActionStatus.SIMULATED,
        message="Sprawa została przekazana do kolejki ogólnej.",
    )