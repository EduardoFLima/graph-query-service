from langchain.messages import HumanMessage


def extract_prompt(state):
    user_prompt = extract_prompt_from(state)
    conversation_history = extract_conversation_history(state["messages"])

    print("🔍 Prompt extracted...")

    return {
        "user_prompt": user_prompt,
        "conversation_history": conversation_history,
        }


def extract_conversation_history(messages) -> str:
    if messages is None:
        return ""

    parsed_messages: list[str] = [
        ("User: " if isinstance(message, HumanMessage) else "AI: ") + message.content
        for message in messages[:-1]
    ]

    return str(parsed_messages)


def extract_prompt_from(state):
    message = state["messages"][-1]

    # Handle messages coming from the inbound adapter (chat service)
    if isinstance(message, HumanMessage):
        prompt = message.content
    else:
        content = message.get("content")
        # Handle messages coming from langsmith studio's chat
        if isinstance(content, list):
            prompt = message["content"][0]["text"]
        else:
            # Handle messages coming from langsmith studio's graph
            prompt = message["content"]
    return prompt
