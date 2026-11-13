from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes.architect import architect_node
from app.agent.nodes.coder import coder_node

workflow = StateGraph(AgentState)

# Define pipeline nodes
workflow.add_node("architect", architect_node)
workflow.add_node("coder", coder_node)

# Set execution flow
workflow.set_entry_point("architect")
workflow.add_edge("architect", "coder")
workflow.add_edge("coder", END)

# EXPORT agent_graph
agent_graph = workflow.compile()