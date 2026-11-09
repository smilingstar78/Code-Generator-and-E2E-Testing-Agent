from app.sandbox.container_runner import run_code_in_sandbox

# Mock generated files: one module and one passing pytest file
mock_files = {
    "math_utils.py": "def add(a, b):\n    return a + b\n",
    "test_math_utils.py": "from math_utils import add\n\ndef test_add():\n    assert add(2, 3) == 5\n"
}

print("Running sandbox test inside Docker...")
exit_code, logs = run_code_in_sandbox(mock_files)

print(f"\nExit Code: {exit_code}")
print("--- Container Output Logs ---")
print(logs)