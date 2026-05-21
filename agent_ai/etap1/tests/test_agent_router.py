# tests/test_agent_router.py

import pytest
from app.agent_router import route_message
from app.schemas import Category, ActionType

@pytest.mark.parametrize(
    "category,text,expected_agent,expected_action",
    [
        (Category.FINANCE, "Mam problem z fakturą", "finance_invoice_agent", ActionType.CREATE_FINANCE_TICKET),
        (Category.FINANCE, "Proszę o przelew za ostatni miesiąc", "finance_invoice_agent", ActionType.CREATE_FINANCE_TICKET),
        (Category.IT_SUPPORT, "Nie mogę zalogować się do VPN", "it_access_agent", ActionType.CREATE_IT_SUPPORT_TICKET),
        (Category.IT_SUPPORT, "Komputer nie działa, drukarka offline", "it_access_agent", ActionType.CREATE_IT_SUPPORT_TICKET),
        (Category.HR, "Chcę złożyć wniosek urlopowy", "hr_leave_agent", ActionType.CREATE_HR_TICKET),
        (Category.HR, "Zwolnienie lekarskie na przyszły tydzień", "hr_leave_agent", ActionType.CREATE_HR_TICKET),
        (Category.OTHER, "Mam pytanie ogólne", "general_agent", ActionType.SEND_TO_GENERAL_QUEUE),
        (Category.FINANCE, "Nie wiem co zrobić", "general_agent", ActionType.SEND_TO_GENERAL_QUEUE)
    ]
)
def test_routing(category, text, expected_agent, expected_action):
    route = route_message(category, text)
    assert route.agent_name == expected_agent
    assert route.action_type == expected_action
    assert route.department == category