import logging

from src.application.ports.outbound.purchase_repository import PurchaseRepository

logger = logging.getLogger(__name__)


def cypher_executor(purchase_repository: PurchaseRepository):
    def cypher_executor_node(state: dict):
        try:
            if "error" in state or "plan_query" not in state:
                return state

            current_step = state["current_step"] if "current_step" in state else None
            results = state["results"] if "results" in state else []

            target_cypher = extract_target_cypher(state)

            logger.info("🧪 ...validating cypher: %s", target_cypher.replace("\n", " "))

            if not purchase_repository.validate_cypher(target_cypher):
                return {
                    "error": "The generated cypher is not valid"
                }

            logger.info("📥 Cypher valid! Fetching results...")

            target_cypher_result = purchase_repository.execute_cypher(target_cypher)

            if target_cypher_result is not None:
                return {
                    "current_step": current_step + 1 if current_step is not None else None,
                    "results": results + [target_cypher_result]
                }

            return {
                "error": f"The following cypher returned any result: '{target_cypher}'",
            }

        except Exception as e:
            return handle_error(e)

    def extract_target_cypher(state: dict) -> str:
        current_step = state["current_step"] if "current_step" in state else None
        cyphers = state["cyphers"] if "cyphers" in state else []

        return cyphers[current_step]

    def handle_error(e: Exception) -> dict[str, str]:
        error = f"❌ Error while executing a cypher: {e}"
        logger.error(error)

        return {
            "error": error,
        }

    return cypher_executor_node
