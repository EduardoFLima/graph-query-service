from datetime import datetime

from langchain.messages import HumanMessage

from src.application.ports.inbound.chat_use_case import ChatUseCase


def resolve_thread_id(thread_id: str) -> str:
    if thread_id is None:
        thread_id = str(datetime.now())
        print("thread_id was null ❌, generated one 🔨", thread_id)
    else:
        print("got an existing thread_id ✅", thread_id)
    return thread_id


class ChatService(ChatUseCase):

    def __init__(self, graph):
        self._graph = graph

    def chat(self, thread_id: str, question: str, user_id: str) -> dict:
        print(f"\n\n===== received a message =====\nmessage:{question}\n")

        messages = [HumanMessage(question)]

        thread_id = resolve_thread_id(thread_id)

        result = self._graph.invoke(
            {"messages": messages},
            config={
                "configurable": {
                    "thread_id": thread_id
                },
            },
            context={"user_id": user_id}
        )

        formatted_messages: list[str] = [
            ("User: " if isinstance(message, HumanMessage) else "AI: ") + message.content
            for message in result["messages"]
        ]

        path = result["path"].value if result.get("path") else None
        preferred_path = result["preferred_path"].value if result.get("preferred_path") else None
        blocked = result["safeguard"].blocked if result.get("safeguard") else None

        print("✅ The resulting path was:", path)
        print("✅ The resulting preferred_path was:", preferred_path)
        print("✅ The safeguard status was:", "blocked" if blocked else "not blocked")

        return {
            "messages": formatted_messages,
            "answer": formatted_messages[-1],
            "blocked": blocked,
            "path": path,
            "preferred_path": preferred_path,
            "thread_id": thread_id,
        }
