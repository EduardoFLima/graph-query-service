from dataclasses import dataclass

from langgraph.graph import MessagesState

from src.application.prompts.plan_query_prompt import PlanQuerySchema


@dataclass
class Safeguard:
    blocked: bool
    reason: str = ""
    analysis: str = ""


class State(MessagesState):
    user_prompt: str
    conversation_history: str
    safeguard: Safeguard
    plan_query: PlanQuerySchema | None = None
