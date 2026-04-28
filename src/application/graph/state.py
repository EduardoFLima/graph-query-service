from dataclasses import dataclass
from enum import Enum

from langgraph.graph import MessagesState


class Path(Enum):
    PATH_A = "path_a"
    PATH_B = "path_b"
    UNKNOWN = "unknown_path"

@dataclass
class Safeguard():
    blocked: bool
    reason: str = ""
    analysis: str = ""


class State(MessagesState):
    user_context: dict
    path: Path
    preferred_path: Path

    safeguard: Safeguard
