from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


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


class SourceChannel(str, Enum):
    CHAT = "CHAT"
    EMAIL = "EMAIL"
    FORM = "FORM"
    API = "API"
    MANUAL = "MANUAL"


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
    source_channel: SourceChannel = SourceChannel.API

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
    route: RouteDecision | None = None


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
    source_channel: SourceChannel = SourceChannel.API
    route: RouteDecision | None = None
    executed_action: ActionResult


class TicketHistoryResponse(BaseModel):
    id: int
    input_text: str
    source_channel: SourceChannel | None = None
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

class EmailAnalyzeRequest(BaseModel):
    from_email: str = Field(..., min_length=3)
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    received_at: datetime | None = None

    @field_validator("subject", "body")
    @classmethod
    def field_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value