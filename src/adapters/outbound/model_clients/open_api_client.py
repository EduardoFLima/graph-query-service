import json
from typing import TypeVar

from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.application.ports.outbound.model_client_port import ModelClientPort
from src.config import Settings

T = TypeVar("T")


class OpenAPIClient(ModelClientPort):

    def __init__(self, settings: Settings):
        self._settings = settings

        self._client = self._instantiate_new_model(self._settings.models)
        self._safeguard_client = self._instantiate_new_model(
            [self._settings.safeguard.model]
        )

    def _instantiate_new_model(self, models):
        return ChatOpenAI(
            api_key=self._settings.openrouter_api_key,
            model=models[0],
            temperature=self._settings.temperature,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": self._settings.http_referer,
                "X-Title": self._settings.x_title,
            },
            extra_body={
                "order": "arcee-ai",
                "models": models,
                "provider": self._settings.provider,
            },
        )

    def send_prompt(
        self, system_prompt: str, user_prompt: str, response_format: type[T]
    ) -> T:
        agent = create_agent(
            model=self._client, tools=[], response_format=response_format
        )

        print("\n⌛...calling the agent...")

        try:
            data = agent.invoke(
                {"messages": [SystemMessage(system_prompt), HumanMessage(user_prompt)]}
            )

            last_ai_message = data["messages"][-2]

            if last_ai_message is not None and isinstance(last_ai_message, AIMessage):
                print(
                    f"\nℹ️ Got a response. The model used was {last_ai_message.response_metadata["model_name"]}",
                )

            structured_response = data.get("structured_response")

            if structured_response is not None:
                return structured_response

        except Exception as e:
            answer = "An error occurred when calling the llm provider"
            print(f"{answer}:", e)

        return None

    def safeguard_check(self, safeguard_prompt: str, response_format: type[T]) -> dict:
        if self._is_safeguard_disabled():
            return self._generate_disabled_response()

        print("\n🛡️...calling the safeguard agent...")

        data = self._safeguard_client.invoke(
            [
                {
                    "role": "user",
                    "content": safeguard_prompt,
                }
            ],
            response_format=response_format,
        )

        model = data.response_metadata["model_name"] if data.response_metadata else None

        print(f"\nℹ️ Got a response. The model used was {model}.")

        return json.loads(data.text)

    def _is_safeguard_disabled(self):
        return not self._settings.safeguard.enabled

    def _generate_disabled_response(self):
        disabled_message = "Safeguard check is disabled"
        print(f"\n⏭️...{disabled_message}...")

        return {"security_status": "SAFE", "analysis": disabled_message}
