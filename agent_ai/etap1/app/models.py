from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)

    category = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=False)
    summary = Column(Text, nullable=False)
    suggested_action = Column(Text, nullable=False)
    source = Column(String(50), nullable=True)

    executed_action_type = Column(String(100), nullable=True)
    executed_action_status = Column(String(50), nullable=True)
    executed_action_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)