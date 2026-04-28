import json

from src.application.graph.message_extractor import extract_prompt_from, extract_conversation_history
from src.application.graph.state import Path
from src.application.ports.outbound.model_client_port import ModelClientPort
from src.application.prompts.identify_intent_prompt import IntentSchema, get_system_prompt, wrap_user_prompt


def identify_intent(model_client: ModelClientPort):
    def identify_intent_node(state: dict):
        dumped_user_context = json.dumps(state["user_context"]) if state.get("user_context") else "None"
        system_prompt = get_system_prompt(dumped_user_context)

        prompt = extract_prompt_from(state)
        conversation_history = extract_conversation_history(state.get("messages"))
        user_prompt = wrap_user_prompt(prompt, conversation_history)

        structured_response = model_client.send_prompt(system_prompt, user_prompt, IntentSchema)

        return {"path": structured_response.path if structured_response else Path.UNKNOWN }

    return identify_intent_node
