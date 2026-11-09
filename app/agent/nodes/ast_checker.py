import ast
from typing import List, Dict
from app.agent.state import AgentState

def validate_ast(files: Dict[str, str]) -> List[str]:
    """
    Scans every Python file in memory using the ast parser.
    Returns a list of human-readable syntax errors if found.
    """
    errors = []
    for filename, code in files.items():
        if filename.endswith(".py"):
            try:
                # ast.parse converts code text into a syntax tree
                ast.parse(code, filename=filename)
            except SyntaxError as se:
                # Capture exact line, column, and error description
                error_msg = f"SyntaxError in {filename} (line {se.lineno}, col {se.offset}): {se.msg}"
                errors.append(error_msg)
            except Exception as e:
                errors.append(f"Parse Error in {filename}: {str(e)}")
    return errors


def ast_checker_node(state: AgentState) -> AgentState:
    """
    LangGraph State Node: Checks files for syntax errors before running Docker.
    """
    files = state.get("files", {})
    syntax_errors = validate_ast(files)

    if syntax_errors:
        # Fast-fail route: record errors and mark exit code as failed (1)
        state["syntax_errors"] = syntax_errors
        state["execution_exit_code"] = 1
        state["test_logs"] = "\n".join(syntax_errors)
    else:
        # Syntax clean: ready for Docker sandbox execution
        state["syntax_errors"] = []
        state["execution_exit_code"] = 0

    return state