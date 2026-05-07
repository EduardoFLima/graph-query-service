import json
from functools import lru_cache
from typing import Any

from pydantic import BaseModel


class AnalyticalResponseSchema(BaseModel):
    analysis: str
    follow_up_questions: list[str]


@lru_cache
def get_system_prompt() -> str:
    system_prompt = {
        "role": "Sales Analytics Reporter - Generate data-driven insights in prose",
        "rules": [
            "CRITICAL: Match the QUESTION language, NOT data language. English question = English answer, Portuguese question = Portuguese answer",
            "Write complete analytical responses using actual data (no placeholders)",
            "Include calculations: percentages, distributions, averages, comparisons",
            "Start with key finding, use bullets for lists, highlight patterns",
            "Provide 2-3 specific follow-up questions in the same language as the original question",
            "Do NOT include queries or apologize for errors",
        ],
        "example": {
            "question": "What is the revenue distribution across purchases?",
            "results": [{"productName": "Meat", "totalRevenue": 25000},
                        {"productName": "Drinks", "totalRevenue": 15000}],
            "analysis": "Strong revenue concentration: **Meat** leads with $25,000 (62.5%), **Drinks** $15,000 (37.5%). Top product sales generates 67% more than second place, indicating strong market demand.",
            "follow_up_questions": ["Which meat has highest recurring sale rate?",
                                    "How many customers purchased Meat?",
                                    "What products are popularly bought together?"],
        }
    }

    return json.dumps(system_prompt)

def get_error_response_prompt(question: str, error: str) -> str:
    error_response_prompt = {
        "question": question,
        "error": error,
        "task": "Explain error in user-friendly terms, suggest alternatives, provide 2-3 better questions",

    }

    return json.dumps(error_response_prompt)

def wrap_user_prompt(
        original_question: str, questions: list[str], cyphers_results: list[Any],
) -> str:
    steps = [
        {
            "step": index + 1,
            "question": questions[index],
            "results": result
        }
        for index, result in enumerate(cyphers_results)
    ]

    user_prompt = {
        "original_question": original_question,
        "task": "Synthesize all steps into coherent narrative, highlight comparisons and patterns",
        "steps": steps,
    }

    return json.dumps(user_prompt)
