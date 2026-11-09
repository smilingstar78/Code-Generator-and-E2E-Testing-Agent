from app.agent.graph import build_graph
from app.agent.state import AgentState

def verify_self_healing_loop():
    print("Initializing Agent Graph to test Fixer Node Self-Healing...")
    app = build_graph()

    # Challenging prompt requiring strict edge case handling
    initial_state: AgentState = {
        "specification": "Create a function `run_length_encode(text)` that encodes 'AABBBCCCC' into '2A3B4C'. If input is empty, return empty string. Write Pytest tests checking multiple consecutive repeats and single character runs.",
        "file_manifest": [],
        "files": {},
        "test_logs": None,
        "execution_exit_code": 1,
        "iterations": 0,
        "is_complete": False,
        "syntax_errors": []
    }

    final_state = app.invoke(initial_state)

    print("\n==========================================")
    print("SELF-HEAL TEST RESULTS")
    print("==========================================")
    print(f"Final Exit Code: {final_state['execution_exit_code']}")
    print(f"Total Fixer Iterations Triggered: {final_state['iterations']}")
    print("\nDocker Logs:\n", final_state.get("test_logs"))

    assert final_state["execution_exit_code"] == 0, "Fixer loop failed to resolve test failures!"
    print("\nSUCCESS: Fixer self-healing loop verified!")

if __name__ == "__main__":
    verify_self_healing_loop()