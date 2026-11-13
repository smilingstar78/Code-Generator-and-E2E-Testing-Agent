from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Dict
from app.agent.state import AgentState

class FixedCodebase(BaseModel):
    files: Dict[str, str] = Field(
        description="Updated dictionary mapping file names to complete corrected source code strings."
    )

llm = ChatGroq(
    model_name="openai/gpt-oss-120b", 
    temperature=0.1,
    max_tokens=4096
)
parser = JsonOutputParser(pydantic_object=FixedCodebase)

prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an expert debugging engineer. Analyze test failure logs and fix code/test files.\n\n"
     "CONSTRAINTS:\n"
     "1. Keep code and tests concise without large docstrings or comments.\n"
     "2. Ensure all test files start with 'test_' and test functions start with 'test_'.\n"
     "3. Output strictly valid JSON.\n\n"
     "{format_instructions}"),
    ("user", 
     "Original Specification: {specification}\n"
     "Current Files: {files}\n"
     "Execution Test Failure Logs:\n{test_logs}")
])

def fixer_node(state: AgentState) -> AgentState:
    specification = state["specification"]
    files = state.get("files", {})
    test_logs = state.get("test_logs", "")

    chain = prompt | llm | parser

    try:
        result = chain.invoke({
            "specification": specification,
            "files": files,
            "test_logs": test_logs,
            "format_instructions": parser.get_format_instructions()
        })

        return {
            **state,
            "files": result.get("files", files)
        }
    except Exception as e:
        print(f"Fixer Node Error: {e}")
        return state