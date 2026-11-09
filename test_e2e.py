from app.agent.graph import build_graph
from app.agent.state import AgentState

def run_e2e_agent():
    print("Initializing Autonomous Code Generator & E2E Agent Graph...")
    app = build_graph()

    initial_state: AgentState = {
        "specification": "Create a Python utility module for validating email formats and strong passwords (at least 8 chars, 1 uppercase, 1 digit, 1 special char). Include a complete Pytest suite testing edge cases.",
        "file_manifest": [],
        "files": {},
        "test_logs": None,
        "execution_exit_code": 1,
        "iterations": 0,
        "is_complete": False,
        "syntax_errors": []
    }

    print("\nExecuting Graph Workflow...")
    final_state = app.invoke(initial_state)

    print("\n==========================================")
    print("WORKFLOW COMPLETE")
    print("==========================================")
    print(f"Final Exit Code: {final_state['execution_exit_code']}")
    print(f"Total Fixer Iterations: {final_state['iterations']}")
    print("\nGenerated File List:", list(final_state['files'].keys()))

    print("\n--- Docker Pytest Output Logs ---")
    print(final_state.get("test_logs", "No logs recorded"))

    assert final_state["execution_exit_code"] == 0, "Agent failed to achieve a passing test suite!"
    print("\nSUCCESS: End-to-End Agent successfully generated, executed, and verified code!")

if __name__ == "__main__":
    run_e2e_agent()