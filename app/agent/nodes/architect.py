import json
import re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.agent.state import AgentState

llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    temperature=0.1,
    max_tokens=2048
)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a Principal Software Architect.\n"
     "Analyze the user specification and return a JSON list of planned filenames.\n"
     "Rule 1: If user asks for Web UI/Frontend, include 'index.html', 'style.css', 'script.js', and 'test_app.py'.\n"
     "Rule 2: If user asks for Python backend, include relevant `.py` modules and at least one test file starting with 'test_'.\n"
     "Return ONLY a JSON array of strings, e.g. [\"auth.py\", \"test_auth.py\"]."),
    ("user", "Specification: {specification}")
])

def architect_node(state: AgentState) -> AgentState:
    specification = state["specification"]
    chain = prompt | llm
    
    try:
        response = chain.invoke({"specification": specification})
        raw_text = response.content if hasattr(response, 'content') else str(response)
        
        match = re.search(r'\[.*?\]', raw_text, re.DOTALL)
        if match:
            manifest = json.loads(match.group(0))
        else:
            manifest = ["main.py", "test_main.py"]
    except Exception as e:
        print(f"Architect Node Exception: {e}")
        manifest = ["main.py", "test_main.py"]

    return {**state, "file_manifest": manifest}