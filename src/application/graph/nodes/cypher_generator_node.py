import logging

from src.application.ports.outbound.model_client_port import ModelClientPort
from src.application.prompts.cypher_generator_prompt import CyperGeneratorSchema, get_system_prompt, wrap_user_prompt

logger = logging.getLogger(__name__)


def cypher_generator(model_client: ModelClientPort):
    def cypher_generator_node(state: dict):
        try:
            if "error" in state or "plan_query" not in state:
                return state

            current_step = state["current_step"] if "current_step" in state else None
            cyphers = state["cyphers"] if "cyphers" in state else []
            plan_query = state["plan_query"]

            question = plan_query.sub_questions[current_step]

            system_prompt = get_system_prompt()
            user_prompt = wrap_user_prompt(question)

            structured_response = model_client.send_prompt(system_prompt, user_prompt, CyperGeneratorSchema)

            if structured_response and structured_response.cypher:
                return {
                    "current_step": current_step + 1 if current_step is not None else None,
                    "cyphers": cyphers + [structured_response.cypher],
                }

            return {
                "error": f"Could not generate a cypher out of the question '{question}'"
            }
        except Exception as e:
            return handle_error(e)

    def handle_error(e: Exception) -> dict[str, str]:
        error = f"❌ Error while generating a cypher: {e}"
        logging.error(error)

        return {
            "error": error,
        }

    return cypher_generator_node
