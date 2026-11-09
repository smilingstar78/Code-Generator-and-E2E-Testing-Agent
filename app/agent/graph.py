from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes.architect import architect_node
from app.agent.nodes.coder import coder_node
from app.agent.nodes.ast_checker import ast_checker_node
from app.agent.nodes.executor import executor_node
from app.agent.nodes.fixer import fixer_node
from app.core.config import settings

def route_after_ast(state: AgentState) -> str:
    """
    Evaluates in-memory AST syntax results.
    If syntax errors exist, fast-fail directly to the Fixer node.
    Otherwise, proceed to Docker Sandbox execution.
    """
    if state.get("syntax_errors"):
        return "fixer"
    return "executor"

def route_after_execution(state: AgentState) -> str:
    """
    Evaluates Docker Pytest test execution results.
    If exit code is 0, execution is complete.
    If non-zero and retries remaining, route to Fixer.
    If max retries reached, terminate with failure state.
    """
    exit_code = state.get("execution_exit_code", 1)
    iterations = state.get("iterations", 0)

    if exit_code == 0:
        return "complete"
    elif iterations >= settings.MAX_RETRY_ITERATIONS:
        return "max_retries_reached"
    else:
        return "fixer"

def build_graph():
    """
    Assembles the complete state machine with nodes and conditional edges.
    """
    workflow = StateGraph(AgentState)

    # Register Nodes
    workflow.add_node("architect", architect_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("ast_checker", ast_checker_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("fixer", fixer_node)

    # Set Linear Entry Flow
    workflow.set_entry_point("architect")
    workflow.add_edge("architect", "coder")
    workflow.add_edge("coder", "ast_checker")

    # Conditional Branch 1: After AST Check
    workflow.add_conditional_edges(
        "ast_checker",
        route_after_ast,
        {
            "executor": "executor",
            "fixer": "fixer"
        }
    )

    # Conditional Branch 2: After Sandbox Execution
    workflow.add_conditional_edges(
        "executor",
        route_after_execution,
        {
            "complete": END,
            "max_retries_reached": END,
            "fixer": "fixer"
        }
    )

    # Fixer Loop Back -> re-validate AST -> re-execute Docker
    workflow.add_edge("fixer", "ast_checker")

    return workflow.compile()