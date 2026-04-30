import logging

from src.application.ports.outbound.model_client_port import ModelClientPort
from src.application.prompts.plan_query_prompt import PlanQuerySchema, get_system_prompt, wrap_user_prompt

logger = logging.getLogger(__name__)


def plan_query(model_client: ModelClientPort):
    def plan_query_node(state: dict):
        try:
            system_prompt = get_system_prompt()
            user_prompt = wrap_user_prompt(state["user_prompt"])

            structured_response = model_client.send_prompt(system_prompt, user_prompt, PlanQuerySchema)

            if structured_response:
                return {"plan_query": structured_response}

            return {
                "error": "No structured response received from the model."
            }
        except Exception as e:
            return handle_error(e)

    def handle_error(e: Exception) -> dict[str, str]:
        error = f"❌ Error while planning the query: {e}"
        logging.error(error)

        return {
            "error": error,
        }

    return plan_query_node
