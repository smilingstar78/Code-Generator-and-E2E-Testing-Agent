from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from app.agent.state import AgentState
from app.core.llm import get_llm

# Define structured Pydantic output schema for the blueprint
class FileSpecification(BaseModel):
    filename: str = Field(description="Name of the file, e.g., 'utils.py' or 'test_utils.py'")
    purpose: str = Field(description="Brief explanation of what functions or tests belong in this file")

class ArchitectureBlueprint(BaseModel):
    file_manifest: List[FileSpecification] = Field(description="List of all source and test files to be generated")
    test_instructions: str = Field(description="Clear rules for edge cases that Pytest must assert")


def architect_node(state: AgentState) -> AgentState:
    """
    LangGraph Node: Takes natural language specification and designs the file architecture.
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(ArchitectureBlueprint)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Principal Software Architect. Your job is to take a user prompt "
            "and design a modular Python application blueprint.\n"
            "Rules:\n"
            "1. Always include at least one main module file (e.g., 'main.py' or 'utils.py').\n"
            "2. Always include a corresponding Pytest test file starting with 'test_' (e.g., 'test_utils.py').\n"
            "3. Keep file structures clean and lightweight."
        )),
        ("user", "User Request: {specification}")
    ])

    chain = prompt_template | structured_llm
    result: ArchitectureBlueprint = chain.invoke({"specification": state["specification"]})

    # Update global state with planned file manifest
    manifest_filenames = [item.filename for item in result.file_manifest]
    state["file_manifest"] = manifest_filenames
    
    return state