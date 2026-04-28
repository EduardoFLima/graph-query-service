import json
from functools import lru_cache

from pydantic import BaseModel, Field

from src.application.graph.state import Path


class SummarizeSchema(BaseModel):
    preferred_path: Path = Field(description="the user preferred path")


@lru_cache
def get_system_prompt() -> str:
    system_prompt = {
        "role": "Conversation summarizer for path preference",
        "task": "Summarize the conversation and identify user preferences",
        "rules": {
            "preferred_path": {
                "description": "the user preferred path",
                "options": {
                    "path_a": {
                        "description": "When during the conversation the user mostly has taken the path A",
                        "keywords": ["first path", "path a", "go left", "first choice"],
                    },
                    "path_b": {
                        "description": "When during the conversation the user mostly has taken the path B",
                        "keywords": ["second path", "path b", "go right", "alternative"],
                    },
                    "unknown": {
                        "description": "When the chosen path is unclear",
                    },
                }
            }
        },
        "extraction_instructions": {
            "preferred_path": [
                "Extract the user preference from the conversation history",
                "The user can pick different paths along the conversation",
                "The preferred path is the one the user takes more often",
                "When the user took paths the same amount of times, take the last path taken"
            ]
        },
        "examples": [
            {
                "input": ["User: I want the first path"],
                "output": {
                    "preferred_path": "path_a"
                },
            },
            {
                "input": ["User: I want the second path"],
                "output": {
                    "preferred_path": "path_b"
                },
            },
            {
                "input": [
                    "User: I want the first path",
                    "AI: You will take the path_a !",
                    "User: I want the path b",
                    "AI: You will take the path_b !"
                ],
                "output": {
                    "preferred_path": "path_b"
                },
            },
            {
                "input": [
                    "User: I want the first path",
                    "AI: You will take the path_a !",
                    "User: I want the path a",
                    "AI: You will take the path_a !",
                    "User: I want the path b",
                    "AI: You will take the path_b !"
                ],
                "output": {
                    "preferred_path": "path_a"
                },
            },
        ],
    }
    return json.dumps(system_prompt)


def wrap_user_prompt(conversation_history: list[str]) -> str:
    user_prompt = {
        "conversation_history": conversation_history,
        "instructions": [
            "Carefully analyze the conversation_history to determine the user preference",
            "Extract all relevant details only from the user prompt",
            "Return only the fields that are present in the conversation_history",
            "Never infer or fabricate values"
        ],
    }

    return json.dumps(user_prompt)
