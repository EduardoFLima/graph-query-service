import json
import types
from datetime import datetime
from functools import lru_cache
from typing import Any

from pydantic import BaseModel

from src.domain.models.product import Product
from src.domain.models.purchase import Purchase
from src.domain.value_objects.product_type import ProductType


class CyperCorrectorSchema(BaseModel):
    corrected_cypher: str


def _extract_attributes_from(some_class) -> dict[Any, str | Any]:
    return {
        key: clean_type(value)
        for key, value in getattr(some_class, "__annotations__", {}).items()
    }


def clean_type(obj):
    if obj is None:
        return "None"
    if isinstance(obj, types.ModuleType):
        return obj.__name__
    if isinstance(obj, type):
        return obj.__name__  # class name
    return type(obj).__name__  # fallback


@lru_cache
def get_system_prompt() -> str:
    system_prompt = {
        "role": "Cypher Corrector - Correct a Neo4j cypher",
        "current_date": datetime.today().strftime("%Y-%m-%d"),
        "Instructions": [
            "Adjust the given cypher only, fix its errors",
            "Use the error message to guide the correction",
        ],
        "rules": [
            "Do not create a new cypher, just fix the given one",
            "Do not infer attributes",
            "Do not fabricate values or attributes"
            "Use elementId() not id()",
            "For conditional counts, use CASE or filter in WITH: COUNT(c) works, but for conditions use: WITH s, COUNT(CASE WHEN pr.progress = 100 THEN 1 END) AS completed",
            "Avoid COUNT{} syntax - use simple COUNT() with CASE statements for conditional counting",
            "Use EXISTS{} for checking existence: WHERE EXISTS { MATCH (s)-[:CONTAINS]->(c) }",
            "Always use AS aliases for all return fields (e.g., s.name AS studentName)",
            "Return flat values (no nested objects), use NULLS LAST when sorting",
            "Filter early in patterns, keep max 3 relationship hops",
            "Return ONLY plain text query (no markdown, no 'cypher' wrapper)",
            "Avoid use year functions and prefer plain numbers",
            "Use datetime, not date"
        ],
        "relationship_types": ["CONTAINS"],
        "domain": {
            "product": _extract_attributes_from(Product),
            "purchase": _extract_attributes_from(Purchase),
            "product_type": [tp.name for tp in ProductType]
        },
        "examples": [
            {
                "cypher": "MATCH (p:Product) RETURN pp",
                "cypher_error": "pp is not recognized",
                "corrected_cypher": "MATCH (p:Product) RETURN p",
            },
            {
                "cypher": "MATCH (p:Purchase) RETURN avgg(p.total_amount)",
                "cypher_error": "avgg is not recognized",
                "corrected_cypher": "MATCH (p:Purchase) RETURN avg(p.total_amount)",
            }
        ],
    }

    return json.dumps(system_prompt)


def get_user_prompt(
        cypher: str,
        cypher_error: str,
) -> str:
    user_prompt = {
        "cypher": cypher,
        "cypher_error": cypher_error
    }

    return json.dumps(user_prompt)
