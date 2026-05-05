from langchain.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from src.application.graph.nodes.cypher_generator_node import cypher_generator
from src.application.graph.nodes.init_state_node import init_state
from src.application.graph.nodes.plan_query_node import plan_query
from src.application.graph.nodes.safeguard_check_node import safeguard_check
from src.application.graph.nodes.summarize_node import summarize
from src.application.graph.state import State
from src.application.ports.outbound.memory_port import MemoryPort
from src.application.ports.outbound.model_client_port import ModelClientPort


def blocked(_):
    return {"messages": [AIMessage("Apologies but a security risk was detected in your last prompt.")]}


def initial_checks_condition(state: dict):
    blocked = state["safeguard"].blocked if state.get("safeguard") else False

    if blocked:
        return "unsafe"

    return "safe"


def iteration_condition(state: dict):
    error = state["error"] if "error" in state else None
    current_step = state["current_step"] if "current_step" in state else None
    total_steps = state["total_steps"] if "total_steps" in state else None

    if error or not current_step or not total_steps:
        return "done"

    # current step is an index whereas total_steps is a count. If they are equal, it means it reached the last index
    if current_step == total_steps:
        return "done"

    return "iterate"


def get_graph_definition(model_client: ModelClientPort, memory_saver: MemoryPort):
    agent_builder = StateGraph(State)

    agent_builder.add_node("init_state", init_state)
    agent_builder.add_node("safeguard_check", safeguard_check(model_client))
    agent_builder.add_node("plan_query", plan_query(model_client))
    agent_builder.add_node("cypher_generator", cypher_generator(model_client))
    agent_builder.add_node("blocked", blocked)
    agent_builder.add_node("summarize", summarize)

    # initial checks
    agent_builder.add_edge(START, "init_state")
    agent_builder.add_edge("init_state", "safeguard_check")
    agent_builder.add_conditional_edges(
        "safeguard_check",
        initial_checks_condition,
        {"safe": "plan_query", "unsafe": "blocked"},
    )

    # after initial checks
    agent_builder.add_edge("plan_query", "cypher_generator")
    agent_builder.add_conditional_edges(
        "cypher_generator",
        iteration_condition,
        {
            "iterate": "cypher_generator",
            "done": "summarize"
        },
    )
    agent_builder.add_edge("blocked", "summarize")
    agent_builder.add_edge("summarize", END)

    return agent_builder.compile(
        checkpointer=memory_saver.get_checkpointer()
    )
