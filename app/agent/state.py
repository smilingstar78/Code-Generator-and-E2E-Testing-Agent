from typing import TypedDict, Dict, Any

class AgentState(TypedDict):
    specification: str
    file_manifest: list
    files: Dict[str, str]
    test_logs: str
    execution_exit_code: int
    fix_attempts: int