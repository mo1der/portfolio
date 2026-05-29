from app.action_router import route_action
from app.schemas import Category, Intent, ActionType


def test_route_finance_create_ticket():
    result = route_action(Category.FINANCE, Intent.CREATE_TICKET)
    assert result == ActionType.CREATE_FINANCE_TICKET


def test_route_it_support_create_ticket():
    result = route_action(Category.IT_SUPPORT, Intent.CREATE_TICKET)
    assert result == ActionType.CREATE_IT_SUPPORT_TICKET


def test_route_hr_create_ticket():
    result = route_action(Category.HR, Intent.CREATE_TICKET)
    assert result == ActionType.CREATE_HR_TICKET


def test_route_other_create_ticket():
    result = route_action(Category.OTHER, Intent.CREATE_TICKET)
    assert result == ActionType.CREATE_OTHER_TICKET


def test_route_finance_check_status():
    result = route_action(Category.FINANCE, Intent.CHECK_STATUS)
    assert result == ActionType.CHECK_FINANCE_STATUS


def test_route_it_support_check_status():
    result = route_action(Category.IT_SUPPORT, Intent.CHECK_STATUS)
    assert result == ActionType.CHECK_IT_SUPPORT_STATUS


def test_route_finance_update_data():
    result = route_action(Category.FINANCE, Intent.UPDATE_DATA)
    assert result == ActionType.UPDATE_FINANCE_DATA


def test_route_finance_complaint():
    result = route_action(Category.FINANCE, Intent.COMPLAINT)
    assert result == ActionType.ESCALATE_FINANCE_COMPLAINT


def test_route_contact_human():
    result = route_action(Category.OTHER, Intent.CONTACT_HUMAN)
    assert result == ActionType.ROUTE_TO_HUMAN


def test_route_thanks():
    result = route_action(Category.IT_SUPPORT, Intent.THANKS)
    assert result == ActionType.NO_ACTION


def test_route_other_intent():
    result = route_action(Category.OTHER, Intent.OTHER)
    assert result == ActionType.SEND_TO_GENERAL_QUEUE