from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from typing import Optional

class ExecutedAction(BaseModel):
    action_type: str
    status: str
    message: str

class Category(str, Enum):
    IT_SUPPORT = "IT_SUPPORT"
    FINANCE = "FINANCE"
    HR = "HR"
    OTHER = "OTHER"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ActionType(str, Enum):
    CREATE_FINANCE_TICKET = "CREATE_FINANCE_TICKET"
    CREATE_IT_SUPPORT_TICKET = "CREATE_IT_SUPPORT_TICKET"
    CREATE_HR_TICKET = "CREATE_HR_TICKET"
    CREATE_OTHER_TICKET = "CREATE_OTHER_TICKET"
    MARK_AS_LOW_PRIORITY = "MARK_AS_LOW_PRIORITY"
    SEND_TO_GENERAL_QUEUE = "SEND_TO_GENERAL_QUEUE"
    ESCALATE_TO_MANAGER = "ESCALATE_TO_MANAGER"


class ActionStatus(str, Enum):
    SIMULATED = "SIMULATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ClassificationRequest(BaseModel):
    text: str = Field(..., min_length=1)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text cannot be empty")
        return value


class RouteDecision(BaseModel):
    agent_name: str
    department: Category
    reason: str
    action_type: ActionType


class ClassificationResponse(BaseModel):
    category: Category
    priority: Priority
    summary: str
    suggested_action: str
    source: str
    route: RouteDecision | None = None  # nowy atrybut


class ActionResult(BaseModel):
    action_type: ActionType
    target_department: Category
    status: ActionStatus
    message: str


class ProcessResponse(BaseModel):
    category: Category
    priority: Priority
    summary: str
    suggested_action: str
    source: str
    route: RouteDecision | None = None  # podpinamy do response
    executed_action: ActionResult


class TicketHistoryResponse(BaseModel):
    id: int
    input_text: str
    category: Category
    priority: Priority
    summary: str
    suggested_action: str
    source: str | None = None
    executed_action_type: str | None = None
    executed_action_status: str | None = None
    executed_action_message: str | None = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }