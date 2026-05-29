from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from app.database import Base

class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    source_channel = Column(String(50), nullable=False, default="API")

    category = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=False)
    intent = Column(String(50), nullable=True)
    ticket_status = Column(String(50), nullable=False, default="NEW")
    summary = Column(Text, nullable=False)
    suggested_action = Column(Text, nullable=False)
    source = Column(String(50), nullable=True)

    executed_action_type = Column(String(100), nullable=True)
    executed_action_status = Column(String(50), nullable=True)
    executed_action_message = Column(Text, nullable=True)

    # NOWE KOLUMNY DLA ROUTINGU AGENTA
    route_agent_name = Column(String(100), nullable=True)
    route_department = Column(String(50), nullable=True)
    route_reason = Column(Text, nullable=True)
    route_action_type = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

