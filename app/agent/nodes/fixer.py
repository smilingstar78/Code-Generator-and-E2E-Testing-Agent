from pydantic import BaseModel, Field
from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from app.agent.state import AgentState
from app.core.llm import get_llm

class FixedCodeOutput(BaseModel):
    files: Dict[str, str] = Field(
        description="Repaired dictionary mapping filenames to updated, fixed Python code strings."
    )
    explanation: str = Field(description="Short summary of what was fixed.")

def fixer_node(state: AgentState) -> AgentState:
    """
    LangGraph Node: Analyzes test logs/errors and patches broken files.
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(FixedCodeOutput)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Senior Software Maintenance & Debugging Engineer.\n"
            "Your code failed syntax validation or unit tests. Analyze the error logs and repair the code.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Fix the root cause identified in the test logs.\n"
            "2. Do not remove test cases unless they contradict the specification.\n"
            "3. Return the entire updated file set with all bugs resolved."
        )),
        ("user", (
            "Original Specification: {specification}\n\n"
            "Current Code Files:\n{files}\n\n"
            "Failure Logs / Traceback:\n{test_logs}\n\n"
            "Please fix the code and return the repaired files."
        ))
    ])

    chain = prompt_template | structured_llm
    result: FixedCodeOutput = chain.invoke({
        "specification": state["specification"],
        "files": str(state["files"]),
        "test_logs": state.get("test_logs", "Unknown error")
    })

    # Update state with repaired code and increment iteration count
    state["files"] = result.files
    state["iterations"] = state.get("iterations", 0) + 1
    return state