from langchain.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from src.application.graph.nodes.cypher_corrector_node import cypher_corrector
from src.application.graph.nodes.cypher_executor_node import cypher_executor
from src.application.graph.nodes.cypher_generator_node import cypher_generator
from src.application.graph.nodes.init_state_node import init_state
from src.application.graph.nodes.plan_query_node import plan_query
from src.application.graph.nodes.safeguard_check_node import safeguard_check
from src.application.graph.nodes.summarize_node import summarize
from src.application.graph.state import State
from src.application.ports.outbound.memory_port import MemoryPort
from src.application.ports.outbound.model_client_port import ModelClientPort
from src.application.ports.outbound.purchase_repository import PurchaseRepository

MAX_CORRECTION_ATTEMPTS = 3


def blocked(_):
    return {"messages": [AIMessage("Apologies but a security risk was detected in your last prompt.")]}


def initial_checks_condition(state: dict):
    blocked = state["safeguard"].blocked if state.get("safeguard") else False

    if blocked:
        return "unsafe"

    return "safe"


def iteration_condition(state: dict):
    needs_correction = state["needs_correction"] if "needs_correction" in state else None
    correction_attempts = state["correction_attempts"] if "correction_attempts" in state else 0

    if needs_correction and correction_attempts < MAX_CORRECTION_ATTEMPTS:
        return "correct"

    error = state["error"] if "error" in state else None
    current_step = state["current_step"] if "current_step" in state else None
    total_steps = state["total_steps"] if "total_steps" in state else None

    if error or current_step is None or total_steps is None:
        return "done"

    # current step is an index whereas total_steps is a count. If they are equal, it means it reached the last index
    if current_step == total_steps:
        return "done"

    return "iterate"


def get_graph_definition(model_client: ModelClientPort,
                         purchase_repository: PurchaseRepository,
                         memory_saver: MemoryPort):
    agent_builder = StateGraph(State)

    agent_builder.add_node("init_state", init_state)
    agent_builder.add_node("safeguard_check", safeguard_check(model_client))
    agent_builder.add_node("plan_query", plan_query(model_client))
    agent_builder.add_node("cypher_generator", cypher_generator(model_client))
    agent_builder.add_node("cypher_executor", cypher_executor(purchase_repository))
    agent_builder.add_node("cypher_corrector", cypher_corrector(model_client))
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

    agent_builder.add_edge("cypher_generator", "cypher_executor")
    agent_builder.add_conditional_edges(
        "cypher_executor",
        iteration_condition,
        {
            "correct": "cypher_corrector",
            "iterate": "cypher_generator",
            "done": "summarize"
        },
    )
    agent_builder.add_edge("cypher_corrector", "cypher_executor")

    agent_builder.add_edge("blocked", "summarize")
    agent_builder.add_edge("summarize", END)

    return agent_builder.compile(
        checkpointer=memory_saver.get_checkpointer()
    )
