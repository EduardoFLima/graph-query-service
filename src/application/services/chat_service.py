import logging
from datetime import datetime

from langchain.messages import HumanMessage

from src.application.ports.inbound.chat_use_case import ChatUseCase

logger = logging.getLogger(__name__)


def resolve_thread_id(thread_id: str) -> str:
    if thread_id is None:
        thread_id = str(datetime.now())
        logger.info("thread_id was null ❌, generated one 🔨 %s", thread_id)
    else:
        logger.info("got an existing thread_id ✅ %s", thread_id)
    return thread_id


class ChatService(ChatUseCase):

    def __init__(self, graph):
        self._graph = graph

    def chat(self, thread_id: str, question: str, user_id: str) -> dict:
        logger.info("\n\n===== received a message =====\nmessage:%s\n", question)

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

        error = result["error"] if "error" in result else None
        blocked = result["safeguard"].blocked if "safeguard" in result else None
        plan_query = result["plan_query"] if "plan_query" in result else None
        complexity = plan_query.complexity if plan_query else None
        reasoning = plan_query.reasoning if plan_query else None
        total_steps = result["total_steps"] if "total_steps" in result else None

        if error:
            logger.error("❌‍️ Error ! %s", error)


        logger.info("👮‍♀️ The safeguard status was: %s", "blocked" if blocked else "not blocked")
        logger.info("🧮 The Complexity: %s", complexity)
        logger.info("🧠 The Reasoning: %s", reasoning)
        logger.info("👟 The total_steps: %s", total_steps)

        return {
            "messages": formatted_messages,
            "answer": formatted_messages[-1],
            "blocked": blocked,
            "thread_id": thread_id,
            "complexity": complexity,
            "reasoning": reasoning,
            "total_steps": total_steps,
            "error": error
        }
