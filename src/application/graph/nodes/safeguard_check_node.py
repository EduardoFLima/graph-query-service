import logging

from src.application.graph.state import Safeguard
from src.application.ports.outbound.model_client_port import ModelClientPort
from src.application.prompts.guardrails_prompt import (
    SafeguardSchema,
    get_safeguard_prompt,
)

logger = logging.getLogger(__name__)


def safeguard_check(model_client: ModelClientPort):
    def safeguard_check_node(state: dict):
        try:
            prompt = state["user_prompt"]

            safeguard_prompt = get_safeguard_prompt(prompt)

            response: dict = model_client.safeguard_check(safeguard_prompt, SafeguardSchema)

            if response["security_status"].upper() == "SAFE":
                return {"safeguard": Safeguard(blocked=False)}

            return {
                "safeguard": Safeguard(
                    blocked=True,
                    reason="Possilbe prompt injection detected.",
                    analysis=response["analysis"] if response.get("analysis") else None,
                )
            }
        except Exception as e:
            logger.error("\n❌ Error: %s", e)

            return {
                "safeguard": Safeguard(
                    blocked=True,
                    reason="Couldn't verify prompt injection. Blocking for being in the safe side."
                )
            }

    return safeguard_check_node
