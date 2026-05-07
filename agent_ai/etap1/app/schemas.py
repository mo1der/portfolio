from enum import Enum

from pydantic import BaseModel


class Category(str, Enum):
    IT_SUPPORT = "IT_SUPPORT"
    FINANCE = "FINANCE"
    HR = "HR"
    OTHER = "OTHER"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ClassificationRequest(BaseModel):
    text: str


class ClassificationResponse(BaseModel):
    category: Category
    priority: Priority
    summary: str
    suggested_action: str