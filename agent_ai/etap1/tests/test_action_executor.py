from app.action_executor import execute_action
from app.schemas import ActionStatus, ActionType, Category


def test_execute_finance_ticket_action():
    result = execute_action(ActionType.CREATE_FINANCE_TICKET)

    assert result.action_type == ActionType.CREATE_FINANCE_TICKET
    assert result.target_department == Category.FINANCE
    assert result.status == ActionStatus.SIMULATED
    assert "finansów" in result.message


def test_execute_it_ticket_action():
    result = execute_action(ActionType.CREATE_IT_TICKET)

    assert result.action_type == ActionType.CREATE_IT_TICKET
    assert result.target_department == Category.IT_SUPPORT
    assert result.status == ActionStatus.SIMULATED
    assert "IT" in result.message


def test_execute_hr_case_action():
    result = execute_action(ActionType.CREATE_HR_CASE)

    assert result.action_type == ActionType.CREATE_HR_CASE
    assert result.target_department == Category.HR
    assert result.status == ActionStatus.SIMULATED
    assert "HR" in result.message


def test_execute_low_priority_action():
    result = execute_action(ActionType.MARK_AS_LOW_PRIORITY)

    assert result.action_type == ActionType.MARK_AS_LOW_PRIORITY
    assert result.target_department == Category.OTHER
    assert result.status == ActionStatus.SIMULATED
    assert "niskiego priorytetu" in result.message


def test_execute_escalation_action():
    result = execute_action(ActionType.ESCALATE_TO_MANAGER)

    assert result.action_type == ActionType.ESCALATE_TO_MANAGER
    assert result.target_department == Category.OTHER
    assert result.status == ActionStatus.SIMULATED
    assert "managera" in result.message


def test_execute_general_queue_action():
    result = execute_action(ActionType.SEND_TO_GENERAL_QUEUE)

    assert result.action_type == ActionType.SEND_TO_GENERAL_QUEUE
    assert result.target_department == Category.OTHER
    assert result.status == ActionStatus.SIMULATED
    assert "kolejki ogólnej" in result.message