from langgraph_dev.mock_memory import MockMemory
from src.adapters.outbound.model_clients.open_api_client import OpenAPIClient
from src.adapters.outbound.persistence.neo4j_purchase_repository import Neo4jPurchaseRepository
from src.config import get_settings
from src.application.graph.factory import build_graph

_settings = get_settings()
_model_client = OpenAPIClient(_settings)
_memory_saver = MockMemory() # With LangGraph API, persistence is handled automatically by the platform
_neo4j_purchase_repository = Neo4jPurchaseRepository(_settings.graph_db.neo4j_uri, _settings.graph_db.neo4j_user, _settings.graph_db.neo4j_password)

graph = build_graph(_model_client, _neo4j_purchase_repository, _memory_saver)
