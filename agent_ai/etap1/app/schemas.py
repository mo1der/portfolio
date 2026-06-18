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

class Intent(str, Enum):
    CREATE_TICKET = "CREATE_TICKET"
    CHECK_STATUS = "CHECK_STATUS"
    UPDATE_DATA = "UPDATE_DATA"
    CONTACT_HUMAN = "CONTACT_HUMAN"
    COMPLAINT = "COMPLAINT"
    THANKS = "THANKS"
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

    CHECK_FINANCE_STATUS = "CHECK_FINANCE_STATUS"
    CHECK_IT_SUPPORT_STATUS = "CHECK_IT_SUPPORT_STATUS"
    CHECK_HR_STATUS = "CHECK_HR_STATUS"
    CHECK_OTHER_STATUS = "CHECK_OTHER_STATUS"

    UPDATE_FINANCE_DATA = "UPDATE_FINANCE_DATA"
    UPDATE_IT_SUPPORT_DATA = "UPDATE_IT_SUPPORT_DATA"
    UPDATE_HR_DATA = "UPDATE_HR_DATA"
    UPDATE_OTHER_DATA = "UPDATE_OTHER_DATA"

    ESCALATE_FINANCE_COMPLAINT = "ESCALATE_FINANCE_COMPLAINT"
    ESCALATE_IT_SUPPORT_COMPLAINT = "ESCALATE_IT_SUPPORT_COMPLAINT"
    ESCALATE_HR_COMPLAINT = "ESCALATE_HR_COMPLAINT"
    ESCALATE_OTHER_COMPLAINT = "ESCALATE_OTHER_COMPLAINT"

    ROUTE_TO_HUMAN = "ROUTE_TO_HUMAN"
    NO_ACTION = "NO_ACTION"


class ActionStatus(str, Enum):
    SIMULATED = "SIMULATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TicketStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class TicketStatusUpdateRequest(BaseModel):
    ticket_status: TicketStatus

class TicketAssignRequest(BaseModel):
    assigned_to: str = Field(..., min_length=1)

    @field_validator("assigned_to")
    @classmethod
    def assigned_to_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Assigned to cannot be empty")
        return value.strip()

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
    default_action_type: ActionType


class ClassificationResponse(BaseModel):
    category: Category
    priority: Priority
    intent: Intent = Intent.OTHER
    summary: str
    suggested_action: str
    source: str
    route: RouteDecision | None = None
    ticket_status: TicketStatus = TicketStatus.NEW


class ActionResult(BaseModel):
    action_type: ActionType
    target_department: Category
    status: ActionStatus
    message: str


class ProcessResponse(BaseModel):
    category: Category
    priority: Priority
    intent: Intent = Intent.OTHER
    summary: str
    suggested_action: str
    source: str
    source_channel: SourceChannel = SourceChannel.API
    route: RouteDecision | None = None
    executed_action: ActionResult
    ticket_status: TicketStatus = TicketStatus.NEW

class TicketHistoryResponse(BaseModel):
    id: int
    input_text: str
    source_channel: SourceChannel | None = None

    category: Category
    priority: Priority
    intent: Intent | None = None
    ticket_status: TicketStatus = TicketStatus.NEW
    assigned_to: str | None = None

    summary: str
    suggested_action: str
    source: str | None = None

    executed_action_type: str | None = None
    executed_action_status: str | None = None
    executed_action_message: str | None = None

    route_agent_name: str | None = None
    route_department: str | None = None
    route_reason: str | None = None
    route_default_action_type: str | None = None

    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class TicketListResponse(BaseModel):
    items: list[TicketHistoryResponse]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool

class TicketStatusHistoryResponse(BaseModel):
    id: int
    ticket_id: int
    old_status: TicketStatus
    new_status: TicketStatus
    changed_by: str
    changed_at: datetime

    model_config = {
        "from_attributes": True
    }

class TicketCommentCreateRequest(BaseModel):
    comment_text: str = Field(..., min_length=1)
    author: str = "SYSTEM"

    @field_validator("comment_text")
    @classmethod
    def comment_text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Comment text cannot be empty")
        return value


class TicketCommentResponse(BaseModel):
    id: int
    ticket_id: int
    comment_text: str
    author: str
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