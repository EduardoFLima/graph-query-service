from langgraph_dev.mock_memory import MockMemory
from src.adapters.outbound.model_clients.open_api_client import OpenAPIClient
from src.config import get_settings
from src.application.graph.factory import build_graph

_settings = get_settings()
_model_client = OpenAPIClient(_settings)
_memory_saver = MockMemory() # With LangGraph API, persistence is handled automatically by the platform

graph = build_graph(_model_client, _memory_saver)
