from app.agent.nodes.ast_checker import validate_ast

# 1. Clean code sample
valid_code = {
    "math_tool.py": "def add(a, b):\n    return a + b\n"
}

# 2. Broken code sample (missing colon after function definition)
broken_code = {
    "math_tool.py": "def add(a, b)\n    return a + b\n"
}

print("--- Testing AST Validator ---")
valid_results = validate_ast(valid_code)
broken_results = validate_ast(broken_code)

print(f"Valid Code Errors: {valid_results}")
print(f"Broken Code Errors: {broken_results}")

assert len(valid_results) == 0, "Valid code should have no errors!"
assert len(broken_results) > 0, "Broken code should catch syntax errors!"

print("\nAST Syntax Validator working perfectly!")