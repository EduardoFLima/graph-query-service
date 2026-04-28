import json
from functools import lru_cache

from pydantic import BaseModel, Field

from src.application.graph.state import Path


class IntentSchema(BaseModel):
    path: Path = Field(description="the path taken")

@lru_cache
def get_system_prompt(user_context: str) -> str:
    system_prompt = {
        "role": "A helpful attendant which supports the user to take their path.",
        "task": "Identify user intent and extract details on the path they want to go",
        "rules": {
            "path_a": {
                "description": "the path A",
                "keywords": ["first path", "path a", "go left", "first choice"],
            },
            "path_b": {
                "description": "the path B",
                "keywords": ["second path", "path b", "go right", "alternative"],
            },
            "unknown": {
                "description": "when the chosen path is unclear",
            },
        },
        "user_context": user_context,
        "extraction_instructions": {
            "path": "Extract the user intent from its prompt, conversation history or from user context",
        },
        "examples": [
            {
                "input": "I want the first path",
                "output": {
                    "path": "path_a"
                },
            },
            {
                "input": "I want some alternative path",
                "output": {
                    "path": "path_b"
                },
            },
            {
                "input": "How are you?",
                "output": {
                    "path": "unknown_path"
                },
            },
        ],
    }
    return json.dumps(system_prompt)


def wrap_user_prompt(prompt: str, conversation_history: str) -> str:
    user_prompt = {
        "request": prompt,
        "conversation_history": conversation_history,
        "instructions": [
            "Carefully analyze the question to determine the user intent",
            "Extract all relevant details only from the user prompt",
            "Return only the fields that are present in the request or coming from user context",
            "Never infer or fabricate values"
        ],
    }

    return json.dumps(user_prompt)
