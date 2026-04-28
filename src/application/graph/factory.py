from src.application.graph.graph import get_graph_definition
from src.application.ports.outbound.memory_port import MemoryPort
from src.application.ports.outbound.model_client_port import ModelClientPort


def build_graph(model_client: ModelClientPort, memory_saver: MemoryPort):
    return get_graph_definition(model_client, memory_saver)