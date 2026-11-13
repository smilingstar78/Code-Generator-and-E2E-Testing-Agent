from app.sandbox.docker_executor import DockerExecutor
from app.agent.state import AgentState

executor_instance = DockerExecutor()

def executor_node(state: AgentState) -> AgentState:
    files = state.get("files", {})
    exit_code, logs = executor_instance.run_tests(files)
    
    iterations = state.get("iterations", 0) + 1
    is_complete = (exit_code == 0)
    
    return {
        **state,
        "execution_exit_code": exit_code,
        "test_logs": logs,
        "iterations": iterations,
        "is_complete": is_complete
    }