import logging

from langchain.messages import HumanMessage

logger = logging.getLogger(__name__)


def init_state(state):
    user_prompt = extract_prompt_from(state)
    conversation_history = extract_conversation_history(state["messages"])

    logger.info("🔍 Initializing state...  Prompt extracted... setting steps info...")

    return {
        "user_prompt": user_prompt,
        "conversation_history": conversation_history,
        "current_step": 0,
        "total_steps": 1,
    }


def extract_conversation_history(messages) -> str:
    if messages is None:
        return ""

    parsed_messages: list[str] = [
        ("User: " if isinstance(message, HumanMessage) else "AI: ") + extract_content_from(message)
        for message in messages[:-1]
    ]

    return str(parsed_messages)


def extract_prompt_from(state):
    last_message = state["messages"][-1]

    return extract_content_from(last_message)


def extract_content_from(message) -> str:
    if getattr(message, "content"):
        content = message.content
    else:
        content = message.get("content")

    # Handle messages coming from the inbound adapter (chat service)
    # Handle messages coming from langsmith studio's graph
    if (isinstance(content, str)):
        return content
    # Handle messages coming from langsmith studio's chat
    if isinstance(content, list):
        content = content[0]["text"]

    return content
