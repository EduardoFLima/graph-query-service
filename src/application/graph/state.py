from dataclasses import dataclass

from langgraph.graph import MessagesState


@dataclass
class Safeguard:
    blocked: bool
    reason: str = ""
    analysis: str = ""


class State(MessagesState):
    user_prompt: str
    conversation_history: str
    safeguard: Safeguard
