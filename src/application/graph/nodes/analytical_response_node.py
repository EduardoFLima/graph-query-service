import logging

from langchain_core.messages import AIMessage

from src.application.ports.outbound.model_client_port import ModelClientPort
from src.application.prompts.analytical_response_prompt import AnalyticalResponseSchema, get_system_prompt, \
    wrap_user_prompt, get_error_response_prompt

logger = logging.getLogger(__name__)


def analytical_response(model_client: ModelClientPort):
    def analytical_response_node(state: dict):
        try:
            logger.info("\n === generating an analytical response 📈 === \n")

            user_prompt = state["user_prompt"]

            if state.get("error") is not None or "plan_query" not in state:
                error = state["error"]
                system_prompt = get_system_prompt()
                user_prompt = get_error_response_prompt(user_prompt, error)

                structured_response = model_client.send_prompt(system_prompt, user_prompt, AnalyticalResponseSchema)

                if structured_response and structured_response.analysis:
                    return {
                        "messages": [AIMessage(content=structured_response.analysis)],
                        "analysis": structured_response.analysis,
                        "follow_up_questions": structured_response.follow_up_questions
                    }

                raise RuntimeError("Model didnt return analysis under structured_response.")

            questions = state["plan_query"].sub_questions
            cyphers_results = state["cyphers_results"] if "cyphers_results" in state else []

            system_prompt = get_system_prompt()
            user_prompt = wrap_user_prompt(user_prompt, questions, cyphers_results)

            structured_response = model_client.send_prompt(system_prompt, user_prompt, AnalyticalResponseSchema)

            if structured_response and structured_response.analysis:
                return {
                    "messages": [AIMessage(content=structured_response.analysis)],
                    "analysis": structured_response.analysis,
                    "follow_up_questions": structured_response.follow_up_questions
                }

            return {
                "error": f"Could not generate an analytical response to the question '{user_prompt}'"
            }
        except Exception as e:
            return handle_error(e)

    def handle_error(e: Exception) -> dict[str, str]:
        error = f"❌ Error while generating an analytical response: {e}"
        logger.error(error)

        return {
            "error": error,
        }

    return analytical_response_node
