import json
from enum import Enum
from functools import lru_cache

from pydantic import BaseModel


class Complexity(Enum):
    SIMPLE = "SIMPLE"
    COMPLEX = "COMPLEX"


class PlanQuerySchema(BaseModel):
    complexity: Complexity
    requiresDecomposition: bool
    subQuestions: list[str]
    reasoning: str


@lru_cache
def get_system_prompt() -> str:
    system_prompt = {
        "role": "Query Complexity Analyzer - Determine if questions need multi-step decomposition",
        "rules": [
            "Generate sub-questions in the SAME language as the input question (ignore data language)",
            "Simple: Single entity, direct retrieval, no group comparisons",
            "Complex: Comparing groups, multiple dependent calculations, relationship analysis",
            "Decompose into max 3 sub-questions, each independently answerable, logically ordered",
        ],
        "examples": [
            {
                "question": "List all available products",
                "complexity": "simple",
                "requiresDecomposition": False,
                "subQuestions": [],
                "reasoning": "Direct retrieval, no comparisons"
            },
            {
                # Compare revenue between high vs low completion courses'
                "question": "Compare average revenue between high quantity vs low quantity purchases ",
                "complexity": "complex",
                "requiresDecomposition": True,
                "subQuestions": ["Average revenue per purchase?",
                                 "Revenue for purchase quantity >= than 20 ?",
                                 "Revenue for purchase quantity < than 20 ?", ],
                "reasoning": "Multiple aggregations + group comparison"},
        ],
    }

    return json.dumps(system_prompt)


def wrap_user_prompt(
        prompt: str,
) -> str:
    return prompt
