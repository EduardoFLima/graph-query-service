from dataclasses import dataclass
from typing import Any

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
    error: str | None = None
    safeguard: Safeguard

    plan_query: PlanQuerySchema | None = None
    cyphers: list[str] | None = None
    cyphers_results: list[Any] | None = None

    needs_correction: bool = False
    correction_attempts: int = 0

    current_step: int = 0
    total_steps: int = 1

    analysis: str | None = None
    follow_up_questions: list[str] | None = None
