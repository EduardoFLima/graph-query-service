from langchain_core.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES


def summarize(state: dict):
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

    return {"messages": new_conversation_history}
