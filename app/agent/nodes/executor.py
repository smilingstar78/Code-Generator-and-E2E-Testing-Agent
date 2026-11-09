from app.agent.state import AgentState
from app.sandbox.container_runner import run_code_in_sandbox

def executor_node(state: AgentState) -> AgentState:
    """
    LangGraph Node: Mounts generated code files into Docker and runs Pytest.
    """
    files = state.get("files", {})
    
    # Run code in hardened Docker sandbox
    exit_code, logs = run_code_in_sandbox(files)
    
    # Update global state with test outcome
    state["execution_exit_code"] = exit_code
    state["test_logs"] = logs
    
    return state