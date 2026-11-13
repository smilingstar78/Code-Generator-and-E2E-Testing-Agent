import tempfile
import os
import subprocess
from typing import Dict, List
from app.agent.state import AgentState

def run_bandit_scan(files: Dict[str, str]) -> List[str]:
    """Scans Python files for security vulnerabilities using Bandit."""
    issues = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for filename, content in files.items():
            if filename.endswith(".py"):
                file_path = os.path.join(temp_dir, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
        
        try:
            res = subprocess.run(
                ["bandit", "-r", temp_dir, "-f", "custom", "--msg-template", "{abspath}:{line}: [{test_id}] {msg}"],
                capture_output=True,
                text=True
            )
            if res.stdout.strip():
                issues = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        except Exception as e:
            issues.append(f"Security Scanner Warning: {str(e)}")
            
    return issues

def security_node(state: AgentState) -> AgentState:
    """Node that performs SAST security checks on generated code."""
    files = state.get("files", {})
    security_issues = run_bandit_scan(files)
    
    # Append security findings to state logs
    log_addition = ""
    if security_issues:
        log_addition = "\n\n--- 🛡️ SECURITY AUDIT FINDINGS ---\n" + "\n".join(security_issues)
    else:
        log_addition = "\n\n--- 🛡️ SECURITY AUDIT: PASSED (No SAST vulnerabilities found) ---"
        
    current_logs = state.get("test_logs") or ""
    
    return {
        **state,
        "test_logs": current_logs + log_addition
    }