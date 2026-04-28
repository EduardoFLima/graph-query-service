from langchain.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from src.application.graph.nodes.identify_intent_node import identify_intent
from src.application.graph.nodes.load_memory_node import load_memory
from src.application.graph.nodes.safeguard_check_node import safeguard_check
from src.application.graph.nodes.summarize_node import summarize
from src.application.graph.state import State, Path
from src.application.ports.outbound.memory_port import MemoryPort
from src.application.ports.outbound.model_client_port import ModelClientPort


def resolve_initial_checks(state):
    return state


def path_a(_):
    return {"messages": [AIMessage("You will take the path_a !")]}


def path_b(_):
    return {"messages": [AIMessage("You will take the path_b !")]}


def unknown_path(_):
    return {
        "messages": [
            AIMessage("Apologies. Couldn't understand the path you want to take.")
        ]
    }


def blocked(_):
    return {"messages": [AIMessage("Apologies but a security risk was detected in your last prompt, no path can be taken.")]}

def initial_checks_condition(state: dict):
    blocked = state["safeguard"].blocked if state.get("safeguard") else False

    if blocked:
        return "unsafe"

    return "safe"


def path_condition(state: dict):
    path = state["path"]
    match path:
        case Path.PATH_A:
            return "path_a"
        case Path.PATH_B:
            return "path_b"
        case _:
            return "unknown_path"


def get_graph_definition(model_client: ModelClientPort, memory_saver: MemoryPort):
    agent_builder = StateGraph(State)

    agent_builder.add_node("load_memory", load_memory)
    agent_builder.add_node("safeguard_check", safeguard_check(model_client))
    agent_builder.add_node("resolve_initial_checks", resolve_initial_checks)
    agent_builder.add_node("identify_intent", identify_intent(model_client))
    agent_builder.add_node("path_a", path_a)
    agent_builder.add_node("path_b", path_b)
    agent_builder.add_node("unknown_path", unknown_path)
    agent_builder.add_node("blocked", blocked)
    agent_builder.add_node("summarize", summarize(model_client))

    # initial checks
    agent_builder.add_edge(START, "load_memory")
    agent_builder.add_edge(START, "safeguard_check")

    agent_builder.add_edge("load_memory", "resolve_initial_checks")
    agent_builder.add_edge("safeguard_check", "resolve_initial_checks")
    agent_builder.add_conditional_edges(
        "resolve_initial_checks",
        initial_checks_condition,
        {"safe": "identify_intent", "unsafe": "blocked"},
    )

    # after initial checks
    agent_builder.add_conditional_edges(
        "identify_intent",
        path_condition,
        {"path_a": "path_a", "path_b": "path_b", "unknown_path": "unknown_path"},
    )
    agent_builder.add_edge("path_a", "summarize")
    agent_builder.add_edge("path_b", "summarize")
    agent_builder.add_edge("unknown_path", "summarize")
    agent_builder.add_edge("blocked", "summarize")
    agent_builder.add_edge("summarize", END)

    return agent_builder.compile(
        checkpointer=memory_saver.get_checkpointer(), store=memory_saver.get_store()
    )
