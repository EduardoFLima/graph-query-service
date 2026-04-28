from langchain_core.messages import RemoveMessage, HumanMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES

from src.application.ports.outbound.model_client_port import ModelClientPort
from src.application.prompts.summarize_prompt import (
    get_system_prompt,
    wrap_user_prompt,
    SummarizeSchema,
)


def summarize(model_client: ModelClientPort):
    def summarize_node(state: dict, runtime):
        messages = state.get("messages")
        shrunk_messages = messages[-6:]

        new_conversation_history = [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *shrunk_messages,
        ]

        blocked = state["safeguard"].blocked if state.get("safeguard") else False
        if blocked:
            return {
                "messages": new_conversation_history,
            }

        conversation_history = [
            ("User: " if isinstance(message, HumanMessage) else "AI: ")
            + message.content
            for message in messages
        ]

        system_prompt = get_system_prompt()
        user_prompt = wrap_user_prompt(conversation_history)

        structured_response = model_client.send_prompt(
            system_prompt, user_prompt, SummarizeSchema
        )
        preferred_path = (
            structured_response.preferred_path if structured_response else None
        )

        user_id = runtime.context["user_id"] if runtime.context else None
        if user_id and preferred_path:
            runtime.store.save_preferred_path(user_id, preferred_path.value)

        return {"messages": new_conversation_history, "preferred_path": preferred_path}

    return summarize_node
