import logging

from src.application.ports.outbound.model_client_port import ModelClientPort
from src.application.prompts.cypher_corrector_prompt import get_system_prompt, get_user_prompt, CyperCorrectorSchema

logger = logging.getLogger(__name__)


def cypher_corrector(model_client: ModelClientPort):
    def cypher_corrector_node(state: dict):
        try:
            cypher_error = state["error"] if "error" in state else None
            current_step = state["current_step"] if "current_step" in state else None
            cyphers = state["cyphers"] if "cyphers" in state else []
            correction_attempts = state["correction_attempts"] if "correction_attempts" in state else 0

            target_cypher = cyphers[current_step]

            system_prompt = get_system_prompt()
            user_prompt = get_user_prompt(target_cypher, cypher_error)

            logger.info("🩹 ...trying to correct cypher")

            structured_response = model_client.send_prompt(system_prompt, user_prompt, CyperCorrectorSchema)

            if structured_response and structured_response.corrected_cypher:
                cyphers[current_step] = structured_response.corrected_cypher

                logger.info("🩹 ...cypher corrected, sending back to executor")

                return {
                    "error": None,
                    "cyphers": cyphers,
                    "needs_correction": False,
                    "correction_attempts": correction_attempts + 1
                }

            return {
                "error": f"Could not correct a cypher out of the cypher '{target_cypher}'"
            }
        except Exception as e:
            return handle_error(e)

    def handle_error(e: Exception) -> dict[str, str]:
        error = f"❌ Error while correcting a cypher: {e}"
        logger.error(error)

        return {
            "error": error,
        }

    return cypher_corrector_node
