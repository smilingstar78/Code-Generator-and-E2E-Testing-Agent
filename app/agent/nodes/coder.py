import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Dict
from app.agent.state import AgentState

class CodeOutput(BaseModel):
    files: Dict[str, str] = Field(
        description="Dictionary mapping filename (e.g. utils.py, test_utils.py) to complete Python source code."
    )

def coder_node(state: AgentState) -> AgentState:
    llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0.1)
    
    parser = JsonOutputParser(pydantic_object=CodeOutput)

    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "You are an expert Python software engineer. Generate production-ready Python modules "
         "and unit tests based on the specification and manifest.\n\n"
         "CRITICAL INSTRUCTIONS FOR CODE GENERATION:\n"
         "1. Return ONLY a valid JSON object matching the requested schema.\n"
         "2. Escape all internal double quotes, backslashes, and newlines properly within JSON strings.\n"
         "3. Do NOT wrap code blocks in markdown fences inside the JSON string values.\n\n"
         "{format_instructions}"),
        ("human", 
         "Specification:\n{specification}\n\nFile Manifest:\n{file_manifest}")
    ])

    chain = prompt | llm | parser

    try:
        result = chain.invoke({
            "specification": state["specification"],
            "file_manifest": json.dumps(state["file_manifest"]),
            "format_instructions": parser.get_format_instructions()
        })
        
        files = result.get("files", {})
    except Exception as e:
        print(f"Coder parsing warning: {e}. Retrying with fallback execution...")
        # Fallback invocation if parser encounters escape issues
        raw_llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0.1)
        raw_res = (prompt | raw_llm).invoke({
            "specification": state["specification"],
            "file_manifest": json.dumps(state["file_manifest"]),
            "format_instructions": parser.get_format_instructions()
        })
        parsed = parser.parse(raw_res.content)
        files = parsed.get("files", {})

    return {
        **state,
        "files": files
    }