from app.agent.state import AgentState
from app.agent.nodes.architect import architect_node
from app.agent.nodes.coder import coder_node

# Initialize initial state
initial_state: AgentState = {
    "specification": "Create a module that reverses words in a sentence and a test file checking empty strings and regular sentences.",
    "file_manifest": [],
    "files": {},
    "test_logs": None,
    "execution_exit_code": 0,
    "iterations": 0,
    "is_complete": False,
    "syntax_errors": []
}

print("1. Running Architect Node...")
state_after_architect = architect_node(initial_state)
print("File Manifest Planned:", state_after_architect["file_manifest"])

print("\n2. Running Coder Node...")
state_after_coder = coder_node(state_after_architect)
print("Generated Files:", list(state_after_coder["files"].keys()))

print("\n--- Code Sample Preview ---")
for filename, content in state_after_coder["files"].items():
    print(f"\n[{filename}]:\n{content[:150]}...")

print("\nPhase 3 Sub-Agents executed successfully!")