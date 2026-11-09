from typing import TypedDict, Dict, Optional, List

class AgentState(TypedDict):
    specification: str                   # 1. The original user request (e.g. "Build a calculator API")
    file_manifest: List[str]             # 2. List of file names planned by Architect (e.g. ["app.py", "test_app.py"])
    files: Dict[str, str]                # 3. Map of file names to their generated code content
    test_logs: Optional[str]             # 4. Stdout/stderr logs from AST syntax checker or Docker Pytest
    execution_exit_code: int             # 5. 0 = All tests passed, 1+ = Something failed
    iterations: int                      # 6. Retry counter (prevents infinite repair loops)
    is_complete: bool                    # 7. Set to True when workflow finishes
    syntax_errors: Optional[List[str]]   # 8. Captured pre-flight AST syntax error messages