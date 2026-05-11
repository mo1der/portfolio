from app.agents import AGENTS
from app.schemas import ClassificationResponse


def route_message(text: str) -> ClassificationResponse:
    agent = AGENTS["classification"]

    return agent(text)