import json
from functools import lru_cache

from pydantic import BaseModel, Field

class PlanQuerySchema(BaseModel):
    plan: str = Field(description="the query plan")

@lru_cache
def get_system_prompt() -> str:
    system_prompt = {
        "role": "Query planner assistant",
        "task": "Identify user intent and break it down in small steps, create a plan for extracting required data to fulfill the user request",
        "rules": {
        },
        "extraction_instructions": {
        },
        "examples": [
            {
                "input": "I want...",
                "output": {
                },
            },
        ],
    }
    return json.dumps(system_prompt)


def wrap_user_prompt(prompt: str) -> str:
    user_prompt = {
        "request": prompt,
        "instructions": [
            "Carefully analyze the question to determine the user intent",
            "Extract all relevant details only from the user prompt",
            "Return only the fields that are present in the request or coming from user context",
            "Never infer or fabricate values"
        ],
    }

    return json.dumps(user_prompt)
