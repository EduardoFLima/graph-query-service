from typing import Annotated

from fastapi import Depends
from langgraph.graph.state import CompiledStateGraph

from src.adapters.outbound.model_clients.open_api_client import OpenAPIClient
from src.adapters.outbound.persistence.postgres_memory import PostgresMemory
from src.application.graph.factory import build_graph
from src.application.ports.inbound.chat_use_case import ChatUseCase
from src.application.ports.outbound.memory_port import MemoryPort
from src.application.ports.outbound.model_client_port import ModelClientPort
from src.application.services.chat_service import ChatService
from src.config import get_settings


def get_model_client(settings=Depends(get_settings)) -> ModelClientPort:
    return OpenAPIClient(settings)


def get_postgres_memory(settings=Depends(get_settings)) -> MemoryPort:
    return PostgresMemory(settings.memory.db_uri)


def get_graph(
        model_client=Depends(get_model_client),
        memory_saver=Depends(get_postgres_memory)
) -> CompiledStateGraph:
    return build_graph(model_client, memory_saver)


def get_chat_service(graph=Depends(get_graph)) -> ChatUseCase:
    return ChatService(graph)


ChatServiceDep = Annotated[ChatUseCase, Depends(get_chat_service)]
