from src.application.graph.graph import get_graph_definition
from src.application.ports.outbound.memory_port import MemoryPort
from src.application.ports.outbound.model_client_port import ModelClientPort
from src.application.ports.outbound.purchase_repository import PurchaseRepository


def build_graph(model_client: ModelClientPort, purchase_repository: PurchaseRepository, memory_saver: MemoryPort):
    return get_graph_definition(model_client, purchase_repository, memory_saver)
