from langchain.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from src.application.graph.nodes.extract_prompt_node import extract_prompt
from src.application.graph.nodes.plan_query_node import plan_query
from src.application.graph.nodes.safeguard_check_node import safeguard_check
from src.application.graph.nodes.summarize_node import summarize
from src.application.graph.state import State
from src.application.ports.outbound.memory_port import MemoryPort
from src.application.ports.outbound.model_client_port import ModelClientPort


def resolve_initial_checks(state):
    return state


def blocked(_):
    return {"messages": [AIMessage("Apologies but a security risk was detected in your last prompt.")]}

def initial_checks_condition(state: dict):
    blocked = state["safeguard"].blocked if state.get("safeguard") else False

    if blocked:
        return "unsafe"

    return "safe"


def get_graph_definition(model_client: ModelClientPort, memory_saver: MemoryPort):
    agent_builder = StateGraph(State)

    agent_builder.add_node("extract_prompt", extract_prompt)
    agent_builder.add_node("safeguard_check", safeguard_check(model_client))
    agent_builder.add_node("resolve_initial_checks", resolve_initial_checks)
    agent_builder.add_node("plan_query", plan_query(model_client))
    agent_builder.add_node("blocked", blocked)
    agent_builder.add_node("summarize", summarize)

    # initial checks
    agent_builder.add_edge(START, "extract_prompt")
    agent_builder.add_edge(START, "safeguard_check")

    agent_builder.add_edge("extract_prompt", "resolve_initial_checks")
    agent_builder.add_edge("safeguard_check", "resolve_initial_checks")
    agent_builder.add_conditional_edges(
        "resolve_initial_checks",
        initial_checks_condition,
        {"safe": "plan_query", "unsafe": "blocked"},
    )

    # after initial checks
    agent_builder.add_edge("plan_query", "summarize")
    agent_builder.add_edge("blocked", "summarize")
    agent_builder.add_edge("summarize", END)

    return agent_builder.compile(
        checkpointer=memory_saver.get_checkpointer()
    )